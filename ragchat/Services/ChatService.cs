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

    public Task EditMessageAsync(string userId, string sessionId, int messageIndex, string newContent)
    {
        // APIの仕様に編集機能がないため、実装しない
        throw new NotImplementedException("Edit functionality is not supported by the API");
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