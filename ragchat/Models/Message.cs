namespace ragchat.Models;

public class Message
{
    public string Content { get; set; } = string.Empty;
    public bool IsUser { get; set; }
    public string? AvatarSrc { get; set; }
    public string? UserName { get; set; }
    public string? Time { get; set; }
    public int? No { get; set; }
    public bool IsEditing { get; set; }
    public string EditValue { get; set; } = string.Empty;
}

public class Session
{
    public string Id { get; set; } = string.Empty;
    public DateTime CreatedAt { get; set; }
    public string Label { get; set; } = string.Empty;
}

public class ChatRequest
{
    public string Content { get; set; } = string.Empty;
    public string? SessionId { get; set; }
    public string? UserId { get; set; }
}

public class ChatResponse
{
    public string Content { get; set; } = string.Empty;
    public string SessionId { get; set; } = string.Empty;
    public int No { get; set; }
}

public class EditMessageRequest
{
    public int MessageIndex { get; set; }
    public string NewContent { get; set; } = string.Empty;
}

public class ConversationHistory
{
    public List<Message> Messages { get; set; } = new();
}

// APIの仕様に合わせたモデルクラス
public class ApiChatMessage
{
    public string Content { get; set; } = string.Empty;
    public string? SessionId { get; set; }
}

public class ApiChatResponse
{
    public int No { get; set; }
    public string Role { get; set; } = string.Empty;
    public string Content { get; set; } = string.Empty;
    public string SessionId { get; set; } = string.Empty;
    public int RequestNo { get; set; }
}

public class ApiChatHistoryResponse
{
    public List<ApiChatMessageHistory> Messages { get; set; } = new();
    public string SessionId { get; set; } = string.Empty;
}

public class ApiChatMessageHistory
{
    public int No { get; set; }
    public string Role { get; set; } = string.Empty;
    public string Content { get; set; } = string.Empty;
} 