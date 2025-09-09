using ragchat.Models;

namespace ragchat.Services;

public interface ISessionService
{
    Task<List<Session>> GetSessionsAsync();
    Task<string> CreateSessionAsync(string? label = null);
    Task AddSessionAsync(Session session);
    Task DeleteSessionAsync(string sessionId);
    Task<Session?> GetSessionAsync(string sessionId);
    Task UpdateSessionLabelAsync(string sessionId, string label);
    Task<List<SessionTitle>> GetSessionTitlesAsync();
    Task DeleteSessionTitleAsync(string sessionId);
} 