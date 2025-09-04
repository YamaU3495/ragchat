using ragchat.Models;
namespace ragchat.Services;

public interface IChatService
{
    Task<ChatResponse> SendMessageAsync(string content, string userId, string? sessionId = null);
    Task<List<Message>> GetConversationHistoryAsync(string userId, string sessionId);
    Task<ChatResponse> EditMessageAsync(string userId, string sessionId, int messageNo, string newContent);
    Task DeleteMessageAsync(string userId, string sessionId, int messageNo);
    Task DeleteAllMessagesAsync(string userId, string sessionId);
}