
using System;
using System.Net.Sockets;
using System.Text;
using System.Text.Json;
using System.IO;
using System.Threading.Tasks;

//class AsyncTcpClient
//{
//    private const string ServerIp = "127.0.0.1";
//    private const int ServerPort = 8888;

//    static async Task Main(string[] args)
//    {
//        try
//        {
//            using TcpClient client = new TcpClient();
//            Console.WriteLine("正在连接服务端...");
//            await client.ConnectAsync(ServerIp, ServerPort);
//            Console.WriteLine("已连接到服务端！");

//            using NetworkStream stream = client.GetStream();
//            using StreamReader reader = new StreamReader(stream, Encoding.UTF8);
//            using StreamWriter writer = new StreamWriter(stream, Encoding.UTF8) { AutoFlush = true };

//            _ = Task.Run(async () =>
//            {
//                try
//                {
//                    while (true)
//                    {
//                        string line = await reader.ReadLineAsync();
//                        if (line == null)
//                        {
//                            Console.WriteLine("服务端已断开连接。");
//                            break;
//                        }

//                        try
//                        {
//                            using JsonDocument doc = JsonDocument.Parse(line);
//                            var root = doc.RootElement;

//                            string status = root.GetProperty("status").GetString();
//                            string message = root.TryGetProperty("message", out var msgProp) ? msgProp.GetString() : "";
//                            Console.WriteLine($"\n📩 服务端响应: [status: {status}] {message}");

//                            if (root.TryGetProperty("detections", out var detections))
//                            {
//                                Console.WriteLine("检测结果:");
//                                foreach (var detection in detections.EnumerateArray())
//                                {
//                                    string label = detection.GetProperty("class").GetString();
//                                    double xCenter = detection.GetProperty("x_center").GetDouble();
//                                    double yCenter = detection.GetProperty("y_center").GetDouble();
//                                    double score = detection.GetProperty("score").GetDouble();

//                                    Console.WriteLine($"  类别: {label}, 中心点: ({xCenter:F2}, {yCenter:F2}), 置信度: {score:P2}");
//                                }
//                            }
//                        }
//                        catch
//                        {
//                            Console.WriteLine($"\n⚠️ 收到非 JSON 响应: {line}");
//                        }

//                        Console.Write(">> ");
//                    }
//                }
//                catch (Exception ex)
//                {
//                    Console.WriteLine($"接收错误: {ex.Message}");
//                }
//            });
//            Console.Write("\nCommand(start_capture / stop_capture / capture / start_display / stop_display / exit_server):\n");
//            while (true)
//            {
//                string command = Console.ReadLine()?.Trim();

//                if (string.IsNullOrWhiteSpace(command))
//                    continue;

//                if (command.ToLower() == "exit_client")
//                    break;

//                var requestObj = new
//                {
//                    command = command,
//                    data = new { timestamp = DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss") }
//                };

//                string jsonMessage = JsonSerializer.Serialize(requestObj);
//                await writer.WriteLineAsync(jsonMessage);  // 自动带换行
//            }

//            Console.WriteLine("断开连接");
//        }
//        catch (Exception ex)
//        {
//            Console.WriteLine($"连接错误: {ex.Message}");
//        }
//    }
//}
