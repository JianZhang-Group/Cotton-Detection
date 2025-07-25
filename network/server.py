import asyncio
from camera.capture import CameraCapture
from recognition import detector
from recognition.detector import ObjectDetector
import cv2

class AsyncServer:
    def __init__(self, host='127.0.0.1', port=8888):
        self.host = host
        self.port = port
        self.camera_capture = CameraCapture()
        self.detector = ObjectDetector(model_path="./models/yolo11n.pt", device='0')

    async def handle_client(self, reader, writer):
        while True:
            data = await reader.read(10000)  # 等待接收数据
            if not data:
                break
            
            message = data.decode()
            addr = writer.get_extra_info('peername')
            print(f"Received {message!r} from {addr}")

            # 根据接收到的消息执行相应的操作
            if message == "start":
                response = "Starting camera capture..."
                self.camera_capture.start_pipeline()
            elif message == "capture":
                response = "Capturing frame..."
                # 获取摄像头帧
                color_image, depth_image = self.camera_capture.get_frame()
                if color_image is not None:
                    results = self.detector.detect_objects(color_image)
                    if results:
                        frame = self.detector.draw_detections(color_image, results)
                        # cv2.imwrite("captured_color_image.jpg", frame)
                        # cv2.imwrite("captured_depth_image.jpg", depth_image)
                    response += " with camera data"
                    response += str(results)
                else:
                    response += " without camera data"
            elif message == "exit":
                response = "Goodbye!"
                self.camera_capture.stop_capture()
            else:
                response = f"Received: {message}"

            print(f"Send: {response}")
            writer.write(response.encode())  # 发送响应
            await writer.drain()  # 等待发送完成

        print("Closing connection")
        writer.close()

    async def start(self):
        server = await asyncio.start_server(
            self.handle_client, self.host, self.port)

        addr = server.sockets[0].getsockname()
        print(f'Server started at {addr}')

        async with server:
            await server.serve_forever()

    def run(self):
        asyncio.run(self.start())

if __name__ == "__main__":
    server = AsyncServer()
    server.run()