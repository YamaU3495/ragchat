using ragchat.Models;
using System.Text.Json;

namespace ragchat.Services;

public class ChatService : IChatService
{
    private readonly HttpClient _httpClient;
    private readonly IConfiguration _configuration;

    public ChatService(HttpClient httpClient, IConfiguration configuration)
    {
        _httpClient = httpClient;
        _configuration = configuration;
    }

    private string GetApiBaseUrl()
    {
        var host = _configuration["Api:Host"] ?? "";
        var port = _configuration["Api:Port"] ?? "";
        if (string.IsNullOrEmpty(host))
        {
            return "/api";
        }
        var protocol = _configuration["Api:Protocol"] ?? "http";
        return !string.IsNullOrEmpty(port) ? $"{protocol}://{host}:{port}" : $"{protocol}://{host}";
    }

    public async Task<ChatResponse> SendMessageAsync(string content, string userId, string? sessionId = null)
    {
        var request = new ChatRequest
        {
            Content = content,
            UserId = userId,
            SessionId = sessionId
        };
        var response = await _httpClient.PostAsJsonAsync($"{GetApiBaseUrl()}/chat", request);
        response.EnsureSuccessStatusCode();
        return await response.Content.ReadFromJsonAsync<ChatResponse>() 
            ?? throw new InvalidOperationException("Failed to deserialize response");
    }

    public async Task<List<Message>> GetConversationHistoryAsync(string userId, string sessionId)
    {
        var response = await _httpClient.GetAsync($"{GetApiBaseUrl()}/chat/history/{userId}/{sessionId}");
        response.EnsureSuccessStatusCode();
        var history = await response.Content.ReadFromJsonAsync<ConversationHistory>();
        return history?.Messages ?? new List<Message>();
    }

    public async Task<ChatResponse> EditMessageAsync(string userId, string sessionId, int messageNo, string newContent)
    {
        var request = new ApiEditMessageRequest
        {
            Content = newContent,
            UserId = userId,
            SessionId = sessionId,
            No = messageNo
        };
        
        var response = await _httpClient.PostAsJsonAsync($"{GetApiBaseUrl()}/chat/edit", request);
        response.EnsureSuccessStatusCode();
        
        var editResponse = await response.Content.ReadFromJsonAsync<ApiEditMessageResponse>();
        if (editResponse == null)
        {
            throw new InvalidOperationException("Failed to deserialize edit response");
        }
        
        return new ChatResponse
        {
            Content = editResponse.Content,
            SessionId = editResponse.SessionId,
            No = editResponse.No
        };
    }

    public async Task DeleteMessageAsync(string userId, string sessionId, int messageNo)
    {
        var response = await _httpClient.DeleteAsync($"{GetApiBaseUrl()}/chat/message/{userId}/{sessionId}/{messageNo}");
        response.EnsureSuccessStatusCode();
    }

    public async Task DeleteAllMessagesAsync(string userId, string sessionId)
    {
        var response = await _httpClient.DeleteAsync($"{GetApiBaseUrl()}/chat/messages/{userId}/{sessionId}");
        response.EnsureSuccessStatusCode();
    }
} 