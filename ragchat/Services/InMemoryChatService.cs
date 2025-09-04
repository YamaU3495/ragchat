using ragchat.Models;

namespace ragchat.Services;

public class InMemoryChatService : IChatService
{
    private readonly Dictionary<string, List<Message>> _sessions = new();
    private int _sessionCounter = 1;

    public Task<ChatResponse> SendMessageAsync(string content, string userId, string? sessionId = null)
    {
        if (string.IsNullOrEmpty(sessionId) || !_sessions.ContainsKey(sessionId))
        {
            sessionId = $"session-{_sessionCounter++}";
            _sessions[sessionId] = new List<Message>();
        }
        var messages = _sessions[sessionId];
        var userMsg = new Message { Content = content, IsUser = true, No = messages.Count + 1 };
        messages.Add(userMsg);
        // 簡易AI応答
        var aiMsg = new Message { Content = $"Echo: {content}", IsUser = false, No = messages.Count + 1 };
        messages.Add(aiMsg);
        return Task.FromResult(new ChatResponse
        {
            Content = aiMsg.Content,
            SessionId = sessionId,
            No = aiMsg.No ?? 0
        });
    }

    public Task<List<Message>> GetConversationHistoryAsync(string userId, string sessionId)
    {
        if (_sessions.TryGetValue(sessionId, out var messages))
            return Task.FromResult(messages.ToList());
        return Task.FromResult(new List<Message>());
    }

    public Task<ChatResponse> EditMessageAsync(string userId, string sessionId, int messageNo, string newContent)
    {
        if (_sessions.TryGetValue(sessionId, out var messages))
        {
            // 指定されたNo以降のメッセージを削除
            messages.RemoveAll(m => m.No >= messageNo);
            
            // 新しいユーザーメッセージを追加
            var userMsg = new Message { Content = newContent, IsUser = true, No = messageNo };
            messages.Add(userMsg);
            
            // 簡易AI応答を追加
            var aiMsg = new Message { Content = $"Echo: {newContent}", IsUser = false, No = messageNo + 1 };
            messages.Add(aiMsg);
            
            return Task.FromResult(new ChatResponse
            {
                Content = aiMsg.Content,
                SessionId = sessionId,
                No = aiMsg.No ?? 0
            });
        }
        
        return Task.FromResult(new ChatResponse
        {
            Content = "セッションが見つかりません",
            SessionId = sessionId,
            No = 0
        });
    }

    public Task DeleteMessageAsync(string userId, string sessionId, int messageNo)
    {
        if (_sessions.TryGetValue(sessionId, out var messages))
        {
            var msg = messages.FirstOrDefault(m => m.No == messageNo);
            if (msg != null) messages.Remove(msg);
        }
        return Task.CompletedTask;
    }

    public Task DeleteAllMessagesAsync(string userId, string sessionId)
    {
        if (_sessions.TryGetValue(sessionId, out var messages))
        {
            messages.Clear();
        }
        return Task.CompletedTask;
    }
} 