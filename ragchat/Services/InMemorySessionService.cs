using ragchat.Models;

namespace ragchat.Services;

public class InMemorySessionService : ISessionService
{
    private readonly Dictionary<string, Session> _sessions = new();
    private int _sessionCounter = 1;

    public Task<List<Session>> GetSessionsAsync()
    {
        return Task.FromResult(_sessions.Values.OrderByDescending(s => s.CreatedAt).ToList());
    }

    public Task<string> CreateSessionAsync(string? label = null)
    {
        var sessionId = $"session-{_sessionCounter++}";
        _sessions[sessionId] = new Session
        {
            Id = sessionId,
            CreatedAt = DateTime.Now,
            Label = label ?? $"チャット {_sessionCounter - 1}"
        };
        return Task.FromResult(sessionId);
    }

    public Task AddSessionAsync(Session session)
    {
        _sessions[session.Id] = session;
        return Task.CompletedTask;
    }

    public Task DeleteSessionAsync(string sessionId)
    {
        _sessions.Remove(sessionId);
        return Task.CompletedTask;
    }

    public Task<Session?> GetSessionAsync(string sessionId)
    {
        _sessions.TryGetValue(sessionId, out var session);
        return Task.FromResult(session);
    }

    public Task UpdateSessionLabelAsync(string sessionId, string label)
    {
        if (_sessions.TryGetValue(sessionId, out var session))
        {
            session.Label = label;
        }
        return Task.CompletedTask;
    }

    public Task<List<SessionTitle>> GetSessionTitlesAsync()
    {
        // InMemorySessionServiceではセッションタイトル機能はサポートしていない
        // 空のリストを返す
        return Task.FromResult(new List<SessionTitle>());
    }

    public Task DeleteSessionTitleAsync(string sessionId)
    {
        throw new NotImplementedException();
    }

} 