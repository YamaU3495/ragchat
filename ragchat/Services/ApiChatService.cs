using ragchat.Models;
using System.Text;
using System.Text.Json;
using System.Text.Json.Serialization;

namespace ragchat.Services;

public class ApiChatService : IChatService
{
    private readonly HttpClient _httpClient;
    private readonly ILogger<ApiChatService> _logger;
    private readonly JsonSerializerOptions _jsonOptions;

    public ApiChatService(IHttpClientFactory httpClientFactory, ILogger<ApiChatService> logger)
    {
        _httpClient = httpClientFactory.CreateClient("ApiClient");
        _logger = logger;
        
        _jsonOptions = new JsonSerializerOptions
        {
            PropertyNamingPolicy = JsonNamingPolicy.SnakeCaseLower,
            DefaultIgnoreCondition = JsonIgnoreCondition.WhenWritingNull
        };
    }

    public async Task<ChatResponse> SendMessageAsync(string content, string userId, string? sessionId = null)
    {
        try
        {
            var requestMessage = new ApiChatMessage
            {
                Content = content,
                UserId = userId,
                SessionId = sessionId
            };

            var json = JsonSerializer.Serialize(requestMessage, _jsonOptions);
            var requestContent = new StringContent(json, Encoding.UTF8, "application/json");

            var response = await _httpClient.PostAsync("/api/chat", requestContent);
            response.EnsureSuccessStatusCode();

            var responseContent = await response.Content.ReadAsStringAsync();
            var apiResponse = JsonSerializer.Deserialize<ApiChatResponse>(responseContent, _jsonOptions);

            if (apiResponse == null)
            {
                throw new InvalidOperationException("API応答のデシリアライズに失敗しました");
            }

            return new ChatResponse
            {
                Content = apiResponse.Content,
                SessionId = apiResponse.SessionId,
                No = apiResponse.No
            };
        }
        catch (HttpRequestException ex)
        {
            _logger.LogError(ex, "API通信エラー: {Message}", ex.Message);
            throw new InvalidOperationException($"API通信エラー: {ex.Message}", ex);
        }
        catch (JsonException ex)
        {
            _logger.LogError(ex, "JSONデシリアライズエラー: {Message}", ex.Message);
            throw new InvalidOperationException($"JSONデシリアライズエラー: {ex.Message}", ex);
        }
    }

    public async Task<List<Message>> GetConversationHistoryAsync(string userId, string sessionId)
    {
        try
        {
            var response = await _httpClient.GetAsync($"/api/chat/history/{userId}/{sessionId}");
            response.EnsureSuccessStatusCode();

            var responseContent = await response.Content.ReadAsStringAsync();
            var apiResponse = JsonSerializer.Deserialize<ApiChatHistoryResponse>(responseContent, _jsonOptions);

            if (apiResponse == null)
            {
                return new List<Message>();
            }

            return apiResponse.Messages.Select(m => new Message
            {
                Content = m.Content,
                IsUser = m.Role == "user",
                No = m.No
            }).ToList();
        }
        catch (HttpRequestException ex)
        {
            _logger.LogError(ex, "API通信エラー: {Message}", ex.Message);
            return new List<Message>();
        }
        catch (JsonException ex)
        {
            _logger.LogError(ex, "JSONデシリアライズエラー: {Message}", ex.Message);
            return new List<Message>();
        }
    }

    public async Task<ChatResponse> EditMessageAsync(string userId, string sessionId, int messageNo, string newContent)
    {
        try
        {
            var requestMessage = new ApiEditMessageRequest
            {
                Content = newContent,
                UserId = userId,
                SessionId = sessionId,
                No = messageNo
            };

            var json = JsonSerializer.Serialize(requestMessage, _jsonOptions);
            var requestContent = new StringContent(json, Encoding.UTF8, "application/json");

            var response = await _httpClient.PostAsync("/api/chat/edit", requestContent);
            response.EnsureSuccessStatusCode();

            var responseContent = await response.Content.ReadAsStringAsync();
            var apiResponse = JsonSerializer.Deserialize<ApiEditMessageResponse>(responseContent, _jsonOptions);

            if (apiResponse == null)
            {
                throw new InvalidOperationException("API応答のデシリアライズに失敗しました");
            }

            return new ChatResponse
            {
                Content = apiResponse.Content,
                SessionId = apiResponse.SessionId,
                No = apiResponse.No
            };
        }
        catch (HttpRequestException ex)
        {
            _logger.LogError(ex, "API通信エラー: {Message}", ex.Message);
            throw new InvalidOperationException($"API通信エラー: {ex.Message}", ex);
        }
        catch (JsonException ex)
        {
            _logger.LogError(ex, "JSONデシリアライズエラー: {Message}", ex.Message);
            throw new InvalidOperationException($"JSONデシリアライズエラー: {ex.Message}", ex);
        }
    }

    public async Task DeleteMessageAsync(string userId, string sessionId, int messageNo)
    {
        try
        {
            var response = await _httpClient.DeleteAsync($"/api/chat/message/{userId}/{sessionId}/{messageNo}");
            response.EnsureSuccessStatusCode();
        }
        catch (HttpRequestException ex)
        {
            _logger.LogError(ex, "API通信エラー: {Message}", ex.Message);
            throw new InvalidOperationException($"API通信エラー: {ex.Message}", ex);
        }
    }

    public async Task DeleteAllMessagesAsync(string userId, string sessionId)
    {
        try
        {
            var response = await _httpClient.DeleteAsync($"/api/chat/messages/{userId}/{sessionId}");
            response.EnsureSuccessStatusCode();
        }
        catch (HttpRequestException ex)
        {
            _logger.LogError(ex, "API通信エラー: {Message}", ex.Message);
            throw new InvalidOperationException($"API通信エラー: {ex.Message}", ex);
        }
    }
} 