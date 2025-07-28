import asyncio
from camera.capture import CameraCapture
from recognition.detector import ObjectDetector
import threading
import cv2
import json
import numpy as np
import torch


def to_serializable(obj):
    """递归转换为可 JSON 序列化的基础类型"""
    if isinstance(obj, torch.Tensor):
        return obj.detach().cpu().numpy().tolist()
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating,)):
        return float(obj)
    if isinstance(obj, dict):
        return {k: to_serializable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [to_serializable(v) for v in obj]
    return obj


class AsyncServer:
    def __init__(self, host='127.0.0.1', port=8888, model_path="./models/model.pt", device='0'):
        self.host = host
        self.port = port
        self.camera_capture = CameraCapture()
        self.detector = ObjectDetector(model_path=model_path, device=device)
        self.running_display = False
        self.display_thread = None

    def start_display_thread(self):
        if self.display_thread and self.display_thread.is_alive():
            return
        self.running_display = True
        self.display_thread = threading.Thread(target=self.display_loop, daemon=True)
        self.display_thread.start()

    def stop_display_thread(self):
        self.running_display = False
        if self.display_thread:
            self.display_thread.join()
            self.display_thread = None

    def display_loop(self):
        while self.running_display:
            color_image, _ = self.camera_capture.get_frame()
            if color_image is None:
                continue
            results = self.detector.detect_objects(color_image)
            frame = self.detector.draw_detections(color_image, results)
            cv2.imshow("Live Detection", frame)
            key = cv2.waitKey(1)
            if key == 27 or cv2.getWindowProperty("Live Detection", cv2.WND_PROP_VISIBLE) < 1:
                self.running_display = False
                break
        cv2.destroyAllWindows()

    async def handle_client(self, reader, writer):
        addr = writer.get_extra_info('peername')
        print(f"Client connected: {addr}")

        buffer = ""
        while True:
            try:
                data = await reader.read(4096)
                print(f"Received data from {addr}: {data.decode()!r}")
                if not data:
                    break
                

                buffer += data.decode()
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)

                    line = line.lstrip('\ufeff').strip()
                    if not line:
                        continue

                    if not line.strip():
                        continue
                    
                    try:
                        message = json.loads(line)
                    except json.JSONDecodeError:
                        response = {"status": "error", "message": "Invalid JSON format"}
                        writer.write((json.dumps(response) + "\n").encode())
                        await writer.drain()
                        continue

                    command = message.get("command")
                    print(f"Received: {command} from {addr}")

                    if command == "start_capture":
                        self.camera_capture.start_pipeline()
                        self.start_display_thread()
                        response = {"status": "ok", "message": "Camera capture started."}

                    elif command == "stop_capture":
                        self.stop_display_thread()
                        self.camera_capture.stop_capture()
                        response = {"status": "ok", "message": "Camera capture stopped."}

                    elif command == "capture":
                        color_image, depth_image = self.camera_capture.get_frame()
                        if color_image is not None:
                            results = self.detector.detect_objects(color_image)
                            sorted_results = self.detector.get_sorted_detections(results)
                            response = {"status": "ok", "detections": to_serializable(sorted_results)}
                        else:
                            response = {"status": "error", "message": "No frame available."}

                    elif command == "start_display":
                        if not self.running_display:
                            self.start_display_thread()
                            response = {"status": "ok", "message": "Display started."}
                        else:
                            response = {"status": "warn", "message": "Display already running."}

                    elif command == "stop_display":
                        if self.running_display:
                            self.stop_display_thread()
                            response = {"status": "ok", "message": "Display stopped."}
                        else:
                            response = {"status": "warn", "message": "Display is not running."}

                    elif command == "exit_server":
                        self.stop_display_thread()
                        self.camera_capture.stop_capture()
                        response = {"status": "ok", "message": "Server stopped."}
                        writer.write((json.dumps(response) + "\n").encode())
                        await writer.drain()
                        return

                    else:
                        response = {"status": "error", "message": f"Unknown command: {command}"}

                    writer.write((json.dumps(response) + "\n").encode())
                    await writer.drain()

            except ConnectionResetError:
                print(f"Client {addr} disconnected unexpectedly.")
                break

        print(f"Closing connection with {addr}")
        writer.close()
        await writer.wait_closed()

    async def start(self):
        server = await asyncio.start_server(self.handle_client, self.host, self.port)
        addr = server.sockets[0].getsockname()
        print(f"Server started at {addr}")
        async with server:
            await server.serve_forever()

    def run(self):
        asyncio.run(self.start())


if __name__ == "__main__":
    server = AsyncServer()
    server.run()
