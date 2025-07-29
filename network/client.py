import asyncio
import json
from datetime import datetime


class DetectionClient:
    def __init__(self, server_ip="127.0.0.1", server_port=8888):
        self.server_ip = server_ip
        self.server_port = server_port
        self.reader = None
        self.writer = None

    async def connect(self):
        try:
            print("正在连接服务端...")
            self.reader, self.writer = await asyncio.open_connection(self.server_ip, self.server_port)
            print("已连接到服务端！")
            return True
        except Exception as ex:
            print(f"连接失败: {ex}")
            return False

    async def _send_request(self, command):
        request_obj = {
            "command": command,
            "data": {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        }
        json_message = json.dumps(request_obj)
        self.writer.write((json_message + "\n").encode("utf-8"))
        await self.writer.drain()

        response_line = await self.reader.readline()
        if not response_line:
            raise ConnectionError("服务端连接已关闭")

        return json.loads(response_line.decode("utf-8").strip())

    async def start_capture(self):
        return await self._send_request("start_capture")

    async def stop_capture(self):
        return await self._send_request("stop_capture")

    async def get_detections(self):
        return await self._send_request("capture")

    async def start_display(self):
        return await self._send_request("start_display")

    async def stop_display(self):
        return await self._send_request("stop_display")

    async def exit_server(self):
        return await self._send_request("exit_server")

    def close(self):
        if self.writer:
            self.writer.close()
            print("已断开连接。")

    # 支持 async with 用法
    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.close()


# 示例主程序（相当于 C# 的 Main）
async def main():
    async with DetectionClient() as client:
        connected = await client.connect()
        if not connected:
            print("连接服务器失败，程序退出")
            return

        start_resp = await client.start_capture()
        print(f"启动结果: {start_resp.get('status', '未知')}")

        for i in range(50):
            detections_resp = await client.get_detections()
            detections = detections_resp.get("detections", [])

            if detections:
                print("检测结果:")
                for det in detections:
                    label = det.get("class", "未知")
                    x = det.get("x_center", 0.0)
                    y = det.get("y_center", 0.0)
                    score = det.get("score", 0.0)

                    print(f"  类别: {label}, 中心: ({x:.2f},{y:.2f}), 置信度: {score:.2%}")

            await asyncio.sleep(1)  # 非阻塞等待1秒

        stop_resp = await client.stop_capture()
        print(f"停止结果: {stop_resp.get('status', '未知')}")


if __name__ == "__main__":
    asyncio.run(main())
