using ragchat.Models;
using Microsoft.JSInterop;
using System.Text.Json;

namespace ragchat.Services;

public class CookieSessionService : ISessionService
{
    private readonly IJSRuntime _jsRuntime;
    private readonly ILogger<CookieSessionService> _logger;
    private const string SessionsCookieName = "ragchat_sessions";
    private const int CookieExpiryDays = 30;

    public CookieSessionService(IJSRuntime jsRuntime, ILogger<CookieSessionService> logger)
    {
        _jsRuntime = jsRuntime;
        _logger = logger;
    }

    private async Task<bool> IsCookieHelperAvailableAsync()
    {
        try
        {
            var result = await _jsRuntime.InvokeAsync<bool>("eval", "typeof window.cookieHelper !== 'undefined'");
            _logger.LogInformation("Cookie helper availability check: {Available}", result);
            return result;
        }
        catch (InvalidOperationException ex) when (ex.Message.Contains("JavaScript interop calls cannot be issued at this time"))
        {
            // This happens during prerendering when JavaScript interop is not available
            _logger.LogDebug("JavaScript interop not available during prerendering, cookie helper unavailable");
            return false;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Cookie helper availability check failed");
            return false;
        }
    }

    public async Task<List<Session>> GetSessionsAsync()
    {
        _logger.LogInformation("GetSessionsAsync called");
        try
        {
            if (!await IsCookieHelperAvailableAsync())
            {
                _logger.LogWarning("Cookie helper not available, returning empty session list");
                return new List<Session>();
            }

            var cookieValue = await _jsRuntime.InvokeAsync<string>("cookieHelper.getCookie", SessionsCookieName);
            _logger.LogInformation("Cookie value retrieved: {CookieValue}", cookieValue ?? "null");
            
            if (string.IsNullOrEmpty(cookieValue))
            {
                return new List<Session>();
            }

            var sessions = JsonSerializer.Deserialize<List<Session>>(cookieValue);
            var result = sessions?.OrderByDescending(s => s.CreatedAt).ToList() ?? new List<Session>();
            _logger.LogInformation("Returning {Count} sessions", result.Count);
            return result;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "セッション一覧取得エラー: {Message}", ex.Message);
            return new List<Session>();
        }
    }

    public async Task<string> CreateSessionAsync(string? label = null)
    {
        _logger.LogInformation("CreateSessionAsync called with label: {Label}", label ?? "null");
        // この実装では明示的なセッション作成は行わない
        // 実際のセッションはメッセージ送信時に自動作成される
        await Task.CompletedTask;
        return string.Empty;
    }

    public async Task AddSessionAsync(Session session)
    {
        _logger.LogInformation("AddSessionAsync called for session: {SessionId}, Label: {Label}", session.Id, session.Label);
        try
        {
            if (!await IsCookieHelperAvailableAsync())
            {
                _logger.LogWarning("Cookie helper not available, cannot save session");
                return;
            }

            var sessions = await GetSessionsAsync();
            _logger.LogInformation("Current session count: {Count}", sessions.Count);
            
            // 既存のセッションがあるかチェック
            var existingSession = sessions.FirstOrDefault(s => s.Id == session.Id);
            if (existingSession != null)
            {
                _logger.LogInformation("Updating existing session: {SessionId}", session.Id);
                // 既存セッションのラベルを更新
                existingSession.Label = session.Label;
                existingSession.CreatedAt = session.CreatedAt;
            }
            else
            {
                _logger.LogInformation("Adding new session: {SessionId}", session.Id);
                // 新しいセッションを追加
                sessions.Add(session);
            }

            var json = JsonSerializer.Serialize(sessions);
            _logger.LogInformation("Serialized sessions JSON: {Json}", json);
            
            await _jsRuntime.InvokeVoidAsync("cookieHelper.setCookie", SessionsCookieName, json, CookieExpiryDays);
            _logger.LogInformation("Cookie set operation completed");
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "セッション追加エラー: {Message}", ex.Message);
        }
    }

    public async Task DeleteSessionAsync(string sessionId)
    {
        _logger.LogInformation("DeleteSessionAsync called for session: {SessionId}", sessionId);
        try
        {
            if (!await IsCookieHelperAvailableAsync())
            {
                _logger.LogWarning("Cookie helper not available, cannot delete session");
                return;
            }

            var sessions = await GetSessionsAsync();
            var session = sessions.FirstOrDefault(s => s.Id == sessionId);
            
            if (session != null)
            {
                sessions.Remove(session);
                var json = JsonSerializer.Serialize(sessions);
                await _jsRuntime.InvokeVoidAsync("cookieHelper.setCookie", SessionsCookieName, json, CookieExpiryDays);
                _logger.LogInformation("Session deleted: {SessionId}", sessionId);
            }
            else
            {
                _logger.LogWarning("Session not found for deletion: {SessionId}", sessionId);
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "セッション削除エラー: {Message}", ex.Message);
        }
    }

    public async Task<Session?> GetSessionAsync(string sessionId)
    {
        _logger.LogInformation("GetSessionAsync called for session: {SessionId}", sessionId);
        try
        {
            var sessions = await GetSessionsAsync();
            var result = sessions.FirstOrDefault(s => s.Id == sessionId);
            _logger.LogInformation("Session found: {Found}", result != null);
            return result;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "セッション取得エラー: {Message}", ex.Message);
            return null;
        }
    }

    public async Task UpdateSessionLabelAsync(string sessionId, string label)
    {
        _logger.LogInformation("UpdateSessionLabelAsync called for session: {SessionId}, Label: {Label}", sessionId, label);
        try
        {
            if (!await IsCookieHelperAvailableAsync())
            {
                _logger.LogWarning("Cookie helper not available, cannot update session label");
                return;
            }

            var sessions = await GetSessionsAsync();
            var session = sessions.FirstOrDefault(s => s.Id == sessionId);
            
            if (session != null)
            {
                session.Label = label;
                var json = JsonSerializer.Serialize(sessions);
                await _jsRuntime.InvokeVoidAsync("cookieHelper.setCookie", SessionsCookieName, json, CookieExpiryDays);
                _logger.LogInformation("Session label updated: {SessionId}", sessionId);
            }
            else
            {
                _logger.LogWarning("Session not found for label update: {SessionId}", sessionId);
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "セッションラベル更新エラー: {Message}", ex.Message);
        }
    }

    public async Task<List<SessionTitle>> GetSessionTitlesAsync()
    {
        _logger.LogInformation("GetSessionTitlesAsync called");
        try
        {
            // CookieSessionServiceではセッションタイトル機能はサポートしていない
            // 空のリストを返す
            _logger.LogWarning("Session titles not supported in CookieSessionService, returning empty list");
            return new List<SessionTitle>();
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "セッションタイトル一覧取得エラー: {Message}", ex.Message);
            return new List<SessionTitle>();
        }
    }
} 