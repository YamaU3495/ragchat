using ragchat.Models;
using System.Text;
using System.Text.Json;
using System.Text.Json.Serialization;

namespace ragchat.Services;

public class ApiSessionService : ISessionService
{
    private readonly HttpClient _httpClient;
    private readonly ILogger<ApiSessionService> _logger;
    private readonly JsonSerializerOptions _jsonOptions;
    
    // API側でセッション管理がない場合の簡易実装（フォールバック）
    private readonly Dictionary<string, Session> _localSessions = new();
    private int _sessionCounter = 1;

    public ApiSessionService(IHttpClientFactory httpClientFactory, ILogger<ApiSessionService> logger)
    {
        _httpClient = httpClientFactory.CreateClient("ApiClient");
        _logger = logger;
        
        _jsonOptions = new JsonSerializerOptions
        {
            PropertyNamingPolicy = JsonNamingPolicy.SnakeCaseLower,
            DefaultIgnoreCondition = JsonIgnoreCondition.WhenWritingNull
        };
    }

    public Task<List<Session>> GetSessionsAsync()
    {
        try
        {
            // API側でセッション一覧取得APIがある場合はこちらを使用
            // var response = await _httpClient.GetAsync("/api/sessions");
            // response.EnsureSuccessStatusCode();
            // var responseContent = await response.Content.ReadAsStringAsync();
            // return JsonSerializer.Deserialize<List<Session>>(responseContent, _jsonOptions) ?? new List<Session>();
            
            // API側でセッション管理がない場合の簡易実装
            return Task.FromResult(_localSessions.Values.OrderByDescending(s => s.CreatedAt).ToList());
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "セッション一覧取得エラー: {Message}", ex.Message);
            return Task.FromResult(_localSessions.Values.OrderByDescending(s => s.CreatedAt).ToList());
        }
    }

    public Task<string> CreateSessionAsync(string? label = null)
    {
        try
        {
            var sessionId = Guid.NewGuid().ToString();
            
            // API側でセッション作成APIがある場合はこちらを使用
            // var createRequest = new { Label = label ?? $"チャット {_sessionCounter++}" };
            // var json = JsonSerializer.Serialize(createRequest, _jsonOptions);
            // var content = new StringContent(json, Encoding.UTF8, "application/json");
            // var response = await _httpClient.PostAsync("/api/sessions", content);
            // response.EnsureSuccessStatusCode();
            // var responseContent = await response.Content.ReadAsStringAsync();
            // var session = JsonSerializer.Deserialize<Session>(responseContent, _jsonOptions);
            // return session?.Id ?? sessionId;
            
            // API側でセッション管理がない場合の簡易実装
            _localSessions[sessionId] = new Session
            {
                Id = sessionId,
                CreatedAt = DateTime.Now,
                Label = label ?? $"チャット {_sessionCounter++}"
            };
            
            return Task.FromResult(sessionId);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "セッション作成エラー: {Message}", ex.Message);
            throw new InvalidOperationException($"セッション作成エラー: {ex.Message}", ex);
        }
    }

    public Task AddSessionAsync(Session session)
    {
        _localSessions[session.Id] = session;
        return Task.CompletedTask;
    }

    public Task DeleteSessionAsync(string sessionId)
    {
        try
        {
            // API側でセッション削除APIがある場合はこちらを使用
            // var response = await _httpClient.DeleteAsync($"/api/sessions/{sessionId}");
            // response.EnsureSuccessStatusCode();
            
            // API側でセッション管理がない場合の簡易実装
            _localSessions.Remove(sessionId);
            return Task.CompletedTask;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "セッション削除エラー: {Message}", ex.Message);
            throw new InvalidOperationException($"セッション削除エラー: {ex.Message}", ex);
        }
    }

    public Task<Session?> GetSessionAsync(string sessionId)
    {
        try
        {
            // API側でセッション取得APIがある場合はこちらを使用
            // var response = await _httpClient.GetAsync($"/api/sessions/{sessionId}");
            // if (response.IsSuccessStatusCode)
            // {
            //     var responseContent = await response.Content.ReadAsStringAsync();
            //     return JsonSerializer.Deserialize<Session>(responseContent, _jsonOptions);
            // }
            
            // API側でセッション管理がない場合の簡易実装
            _localSessions.TryGetValue(sessionId, out var session);
            return Task.FromResult(session);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "セッション取得エラー: {Message}", ex.Message);
            return Task.FromResult<Session?>(null);
        }
    }

    public Task UpdateSessionLabelAsync(string sessionId, string label)
    {
        try
        {
            // API側でセッション更新APIがある場合はこちらを使用
            // var updateRequest = new { Label = label };
            // var json = JsonSerializer.Serialize(updateRequest, _jsonOptions);
            // var content = new StringContent(json, Encoding.UTF8, "application/json");
            // var response = await _httpClient.PutAsync($"/api/sessions/{sessionId}", content);
            // response.EnsureSuccessStatusCode();
            
            // API側でセッション管理がない場合の簡易実装
            if (_localSessions.TryGetValue(sessionId, out var session))
            {
                session.Label = label;
            }
            
            return Task.CompletedTask;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "セッションラベル更新エラー: {Message}", ex.Message);
            throw new InvalidOperationException($"セッションラベル更新エラー: {ex.Message}", ex);
        }
    }
} 