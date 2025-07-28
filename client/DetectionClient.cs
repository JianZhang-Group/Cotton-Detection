using System;
using System.Net.Sockets;
using System.Text;
using System.Text.Json;
using System.IO;
using System.Threading.Tasks;

public class DetectionClient : IDisposable
{
    private readonly string _serverIp = "127.0.0.1";
    private readonly int _serverPort = 8888;
    // ... 构造和 ConnectAsync 保持不变

    private TcpClient _client;
    private NetworkStream _stream;
    private StreamReader _reader;
    private StreamWriter _writer;

    public async Task<bool> ConnectAsync()
    {
        _client = new TcpClient();
        try
        {
            Console.WriteLine("正在连接服务端...");
            await _client.ConnectAsync(_serverIp, _serverPort);
            Console.WriteLine("已连接到服务端！");

            _stream = _client.GetStream();
            _reader = new StreamReader(_stream, new UTF8Encoding(false));
            _writer = new StreamWriter(_stream, new UTF8Encoding(false)) { AutoFlush = true };

            return true;
        }
        catch (Exception ex)
        {
            Console.WriteLine($"连接失败: {ex.Message}");
            return false;
        }
    }

    // 通用请求-响应函数
    private async Task<JsonElement> SendRequestAsync(string command)
    {
        var requestObj = new
        {
            command = command,
            data = new { timestamp = DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss") }
        };

        string jsonMessage = JsonSerializer.Serialize(requestObj);
        await _writer.WriteAsync(jsonMessage + "\n");

        // 等待服务端返回
        string responseLine = await _reader.ReadLineAsync();
        if (responseLine == null)
            throw new IOException("服务端连接已关闭");

        using JsonDocument doc = JsonDocument.Parse(responseLine);
        return doc.RootElement.Clone();  // 克隆避免 using 后被释放
    }

    public async Task<JsonElement> StartCaptureAsync() => await SendRequestAsync("start_capture");
    public async Task<JsonElement> StopCaptureAsync() => await SendRequestAsync("stop_capture");
    public async Task<JsonElement> GetDetectionsAsync() => await SendRequestAsync("capture");
    public async Task<JsonElement> StartDisplayAsync() => await SendRequestAsync("start_display");
    public async Task<JsonElement> StopDisplayAsync() => await SendRequestAsync("stop_display");
    public async Task<JsonElement> ExitServerAsync() => await SendRequestAsync("exit_server");

    public void Dispose()
    {
        _writer?.Dispose();
        _reader?.Dispose();
        _stream?.Dispose();
        _client?.Close();
        Console.WriteLine("已断开连接。");
    }
}
