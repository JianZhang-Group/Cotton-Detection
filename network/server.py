import asyncio
from camera.capture import CameraCapture
from recognition.detector import ObjectDetector
import threading
import cv2

class AsyncServer:
    def __init__(self, host='127.0.0.1', port=8888):
        self.host = host
        self.port = port
        self.camera_capture = CameraCapture()
        self.detector = ObjectDetector(model_path="./models/model.pt", device='cpu')
        self.running_display = False
        self.display_thread = None

    def start_display_thread(self):
        """启动实时显示线程"""
        if self.display_thread and self.display_thread.is_alive():
            print("Display thread already running.")
            return

        self.running_display = True
        self.display_thread = threading.Thread(target=self.display_loop)
        self.display_thread.start()

    def stop_display_thread(self):
        """停止实时显示线程"""
        self.running_display = False
        if self.display_thread:
            self.display_thread.join()
            self.display_thread = None

    def display_loop(self):
        """持续获取帧并显示图像"""
        while self.running_display:
            color_image, _ = self.camera_capture.get_frame()
            if color_image is None:
                continue

            results = self.detector.detect_objects(color_image)
            frame = self.detector.draw_detections(color_image, results)
            cv2.imshow("Live Detection", frame)

            # 退出窗口支持 ESC 或窗口被关闭
            key = cv2.waitKey(1)
            if key == 27 or cv2.getWindowProperty("Live Detection", cv2.WND_PROP_VISIBLE) < 1:
                self.running_display = False
                break

        cv2.destroyAllWindows() 

    async def handle_client(self, reader, writer):
        while True:
            data = await reader.read(10000)  # 等待接收数据
            if not data:
                break
            
            message = data.decode()
            addr = writer.get_extra_info('peername')
            print(f"Received {message!r} from {addr}")

            # 根据接收到的消息执行相应的操作
            if message == "start_capture":
                response = "Starting camera capture..."
                self.camera_capture.start_pipeline()
                self.start_display_thread()

            elif message == "stop_capture":
                response = "Goodbye!"
                self.stop_display_thread()
                self.camera_capture.stop_capture()

            elif message == "capture":
                # 获取摄像头帧
                color_image, depth_image = self.camera_capture.get_frame()
                if color_image is not None:
                    results = self.detector.detect_objects(color_image)
                    sorted_results = self.detector.get_sorted_detections(results)
                    response = str(sorted_results)
                else:
                    response = "None"

            elif message == "start_display":
                if not self.running_display:
                    self.start_display_thread()
                    response = "Display started."
                else:
                    response = "Display already running."

            elif message == "stop_display":
                if self.running_display:
                    self.stop_display_thread()
                    response = "Display stopped."
                else:
                    response = "Display is not running."

            elif message == "exit_server":
                self.stop_display_thread()
                self.camera_capture.stop_capture()
                response = "Server stopped."
                break

            else:
                response = f"Received: {message}"

            print(f"Send: {response}")
            writer.write(response.encode())  # 发送响应
            await writer.drain()  # 等待发送完成

        print("Closing connection")
        writer.close()
    
        # 创建服务器停止动作
        await writer.wait_closed()


    async def start(self):
        server = await asyncio.start_server(
            self.handle_client, self.host, self.port)

        addr = server.sockets[0].getsockname()
        print(f'Server started at {addr}')

        async with server:
            await server.serve_forever()

    def run(self):
        asyncio.run(self.start())

    def stop(self):
        """停止服务器"""
        if self.display_thread and self.display_thread.is_alive():
            self.stop_display_thread()
        print("Server stopped.")

if __name__ == "__main__":
    server = AsyncServer()
    server.run()