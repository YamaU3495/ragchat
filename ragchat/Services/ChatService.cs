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

    public async Task<ChatResponse> SendMessageAsync(string content, string? sessionId = null)
    {
        var request = new ChatRequest
        {
            Content = content,
            SessionId = sessionId
        };
        var response = await _httpClient.PostAsJsonAsync($"{GetApiBaseUrl()}/chat", request);
        response.EnsureSuccessStatusCode();
        return await response.Content.ReadFromJsonAsync<ChatResponse>() 
            ?? throw new InvalidOperationException("Failed to deserialize response");
    }

    public async Task<List<Message>> GetConversationHistoryAsync(string sessionId)
    {
        var response = await _httpClient.GetAsync($"{GetApiBaseUrl()}/chat/history/{sessionId}");
        response.EnsureSuccessStatusCode();
        var history = await response.Content.ReadFromJsonAsync<ConversationHistory>();
        return history?.Messages ?? new List<Message>();
    }

    public async Task EditMessageAsync(string sessionId, int messageIndex, string newContent)
    {
        var request = new EditMessageRequest
        {
            MessageIndex = messageIndex,
            NewContent = newContent
        };
        var response = await _httpClient.PostAsJsonAsync($"{GetApiBaseUrl()}/chat/edit/{sessionId}", request);
        response.EnsureSuccessStatusCode();
    }

    public async Task DeleteMessageAsync(string sessionId, int messageNo)
    {
        var response = await _httpClient.DeleteAsync($"{GetApiBaseUrl()}/chat/message/{sessionId}/{messageNo}");
        response.EnsureSuccessStatusCode();
    }

    public async Task DeleteAllMessagesAsync(string sessionId)
    {
        var response = await _httpClient.DeleteAsync($"{GetApiBaseUrl()}/chat/session/{sessionId}");
        response.EnsureSuccessStatusCode();
    }
} 