using System.Net.Sockets;
using System.Text;
using System.Text.Json;
using System.Threading;

class Program
{
    static async Task Main()
    {
        using var client = new DetectionClient();
        bool connected = await client.ConnectAsync();
        if (!connected)
        {
            Console.WriteLine("连接服务器失败，程序退出");
            return;
        }

        var startResp = await client.StartCaptureAsync();
        Console.WriteLine($"启动结果: {startResp.GetProperty("status").GetString()}");
        for (int i = 0; i < 100; i++)
        {
            var detectionsResp = await client.GetDetectionsAsync();

            if (detectionsResp.TryGetProperty("detections", out var detections))
            {
                Console.WriteLine("检测结果:");
                foreach (var det in detections.EnumerateArray())
                {
                    string label = det.GetProperty("class").GetString();
                    double x = det.GetProperty("x_center").GetDouble();
                    double y = det.GetProperty("y_center").GetDouble();
                    double score = det.GetProperty("score").GetDouble();

                    Console.WriteLine($"  类别: {label}, 中心: ({x:F2},{y:F2}), 置信度: {score:P2}");
                }
            }
            Thread.Sleep(1000);
        }

        var stopResp = await client.StopCaptureAsync();
        Console.WriteLine($"停止结果: {stopResp.GetProperty("status").GetString()}");

        await client.ExitServerAsync();
    }
}
