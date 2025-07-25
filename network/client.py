import asyncio

class AsyncClient:
    def __init__(self, host='127.0.0.1', port=8888):
        self.host = host
        self.port = port

    async def send_data(self):
        reader, writer = await asyncio.open_connection(self.host, self.port)

        while True:
            message = input("Enter message: ")

            writer.write(message.encode())  # 发送数据
            await writer.drain()  # 等待发送完成

            print(f"Send: {message!r}")

            # 等待接收响应
            data = await reader.read(10000)
            print(f"Received: {data.decode()!r}")

            # 根据不同的响应结果执行操作
            if data.decode() == "pong":
                print("Received pong, doing something special...")
            else:
                print("Received other response")

        writer.close()
        await writer.wait_closed()

    def run(self):
        asyncio.run(self.send_data())

if __name__ == "__main__":
    client = AsyncClient()
    client.run()