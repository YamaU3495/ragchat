using ragchat.Models;
namespace ragchat.Services;

public interface IChatService
{
    Task<ChatResponse> SendMessageAsync(string content, string? sessionId = null);
    Task<List<Message>> GetConversationHistoryAsync(string sessionId);
    Task EditMessageAsync(string sessionId, int messageIndex, string newContent);
    Task DeleteMessageAsync(string sessionId, int messageNo);
}