using ragchat.Models;
using System.Text;
using System.Text.Json;
using System.Text.Json.Serialization;
using Microsoft.AspNetCore.Http;
using System.Linq;

namespace ragchat.Services;

public class ApiSessionService : ISessionService
{
    private readonly HttpClient _httpClient;
    private readonly ILogger<ApiSessionService> _logger;
    private readonly JsonSerializerOptions _jsonOptions;
    private readonly IHttpContextAccessor _httpContextAccessor;
    
    // API側でセッション管理がない場合の簡易実装（フォールバック）
    private readonly Dictionary<string, Session> _localSessions = new();
    private int _sessionCounter = 1;

    public ApiSessionService(IHttpClientFactory httpClientFactory, ILogger<ApiSessionService> logger, IHttpContextAccessor httpContextAccessor)
    {
        _httpClient = httpClientFactory.CreateClient("ApiClient");
        _logger = logger;
        _httpContextAccessor = httpContextAccessor;
        
        _jsonOptions = new JsonSerializerOptions
        {
            PropertyNamingPolicy = JsonNamingPolicy.SnakeCaseLower,
            DefaultIgnoreCondition = JsonIgnoreCondition.WhenWritingNull
        };
    }

    public async Task<List<Session>> GetSessionsAsync()
    {
        try
        {
            var userId = GetCurrentUserId();
            if (string.IsNullOrEmpty(userId))
            {
                _logger.LogWarning("User ID not available, returning empty session list");
                return new List<Session>();
            }

            _logger.LogInformation("Fetching sessions for user: {UserId}", userId);
            var response = await _httpClient.GetAsync($"/api/chat/sessions/{userId}");
            
            if (response.IsSuccessStatusCode)
            {
                var responseContent = await response.Content.ReadAsStringAsync();
                _logger.LogInformation("API response: {Response}", responseContent);
                
                var apiResponse = JsonSerializer.Deserialize<ApiSessionsResponse>(responseContent, _jsonOptions);
                if (apiResponse?.SessionIds != null)
                {
                    // SessionIDのリストをSession オブジェクトのリストに変換
                    var sessions = new List<Session>();
                    foreach (var sessionId in apiResponse.SessionIds)
                    {
                        var label = await GenerateDefaultLabelAsync(userId, sessionId);
                        sessions.Add(new Session
                        {
                            Id = sessionId,
                            CreatedAt = DateTime.Now, // APIにはCreatedAtがないため現在時刻を設定
                            Label = label
                        });
                    }
                    
                    var result = sessions.OrderByDescending(s => s.CreatedAt).ToList();
                    _logger.LogInformation("Retrieved {Count} sessions from API", result.Count);
                    return result;
                }
            }
            else
            {
                _logger.LogWarning("API call failed with status: {StatusCode}", response.StatusCode);
            }
            
            // APIから取得できない場合はローカルセッションを返す
            _logger.LogInformation("Falling back to local sessions");
            return _localSessions.Values.OrderByDescending(s => s.CreatedAt).ToList();
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "セッション一覧取得エラー: {Message}", ex.Message);
            return _localSessions.Values.OrderByDescending(s => s.CreatedAt).ToList();
        }
    }

    private string? GetCurrentUserId()
    {
        var context = _httpContextAccessor.HttpContext;
        if (context?.User?.Identity?.IsAuthenticated == true)
        {
            var user = context.User;
            return user.FindFirst("sub")?.Value ?? 
                   user.FindFirst("nameidentifier")?.Value ?? 
                   user.FindFirst("http://schemas.xmlsoap.org/ws/2005/05/identity/claims/nameidentifier")?.Value;
        }
        return null;
    }

    private async Task<string> GenerateDefaultLabelAsync(string userId, string sessionId)
    {
        try
        {
            // セッションのメッセージ履歴を取得
            var response = await _httpClient.GetAsync($"/api/chat/history/{userId}/{sessionId}");
            
            if (response.IsSuccessStatusCode)
            {
                var responseContent = await response.Content.ReadAsStringAsync();
                var apiResponse = JsonSerializer.Deserialize<ApiChatHistoryResponse>(responseContent, _jsonOptions);
                
                if (apiResponse?.Messages != null)
                {
                    // No=1のユーザーメッセージを検索
                    var firstUserMessage = apiResponse.Messages
                        .Where(m => m.Role == "user" && m.No == 1)
                        .FirstOrDefault();
                    
                    if (firstUserMessage != null && !string.IsNullOrEmpty(firstUserMessage.Content))
                    {
                        // メッセージの先頭8文字を取得（改行や空白を除去）
                        var cleanContent = firstUserMessage.Content.Trim().Replace("\n", " ").Replace("\r", "");
                        const int maxLength = 8;
                        
                        if (cleanContent.Length <= maxLength)
                        {
                            return cleanContent;
                        }
                        
                        return cleanContent.Substring(0, maxLength);
                    }
                }
            }
            
            _logger.LogWarning("Could not get message history for session {SessionId}, using fallback label", sessionId);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error getting message history for label generation: {Message}", ex.Message);
        }
        
        // フォールバック: セッションIDの最初の8文字を使用
        var shortId = sessionId.Length > 8 ? sessionId.Substring(0, 8) : sessionId;
        return $"Chat {shortId}";
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

    public async Task<List<SessionTitle>> GetSessionTitlesAsync()
    {
        try
        {
            var userId = GetCurrentUserId();
            if (string.IsNullOrEmpty(userId))
            {
                _logger.LogWarning("User ID not available, returning empty session titles list");
                return new List<SessionTitle>();
            }

            _logger.LogInformation("Fetching session titles for user: {UserId}", userId);
            var response = await _httpClient.GetAsync($"/api/chat/sessions/titles/{userId}");
            
            if (response.IsSuccessStatusCode)
            {
                var responseContent = await response.Content.ReadAsStringAsync();
                _logger.LogInformation("Session titles API response: {Response}", responseContent);
                
                var apiResponse = JsonSerializer.Deserialize<SessionTitlesListResponse>(responseContent, _jsonOptions);
                if (apiResponse?.Sessions != null)
                {
                    _logger.LogInformation("Retrieved {Count} session titles from API", apiResponse.Sessions.Count);
                    return apiResponse.Sessions;
                }
            }
            else
            {
                _logger.LogWarning("Session titles API call failed with status: {StatusCode}", response.StatusCode);
            }
            
            return new List<SessionTitle>();
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "セッションタイトル一覧取得エラー: {Message}", ex.Message);
            return new List<SessionTitle>();
        }
    }
} 