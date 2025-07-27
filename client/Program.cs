using System;
using System.Net.Sockets;
using System.Text;
using System.Threading.Tasks;

class AsyncTcpClient
{
    private const string ServerIp = "127.0.0.1"; // 服务端 IP
    private const int ServerPort = 8888;         // 服务端端口

    static async Task Main(string[] args)
    {
        try
        {
            using TcpClient client = new TcpClient();
            Console.WriteLine("正在连接服务端...");

            await client.ConnectAsync(ServerIp, ServerPort);
            Console.WriteLine("已连接到服务端！");

            using NetworkStream stream = client.GetStream();

            // 启动接收消息的任务
            _ = Task.Run(() => ReceiveMessagesAsync(stream));

            // 循环读取用户输入并发送消息
            while (true)
            {
                Console.Write("你说: ");
                string message = Console.ReadLine();

                if (string.IsNullOrWhiteSpace(message))
                    continue;

                if (message.ToLower() == "exit")
                    break;

                byte[] dataToSend = Encoding.UTF8.GetBytes(message);
                await stream.WriteAsync(dataToSend, 0, dataToSend.Length);
            }

            Console.WriteLine("断开连接");
        }
        catch (Exception ex)
        {
            Console.WriteLine($"连接错误: {ex.Message}");
        }
    }

    private static async Task ReceiveMessagesAsync(NetworkStream stream)
    {
        byte[] buffer = new byte[4096];

        try
        {
            while (true)
            {
                int bytesRead = await stream.ReadAsync(buffer, 0, buffer.Length);
                if (bytesRead == 0)
                {
                    Console.WriteLine("服务端已断开连接。");
                    break;
                }

                string response = Encoding.UTF8.GetString(buffer, 0, bytesRead);
                Console.WriteLine($"\n服务端说: {response}\n你说: ");
            }
        }
        catch (Exception ex)
        {
            Console.WriteLine($"接收错误: {ex.Message}");
        }
    }
}
