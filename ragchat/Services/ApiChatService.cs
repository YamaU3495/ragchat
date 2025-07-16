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

    public async Task<ChatResponse> SendMessageAsync(string content, string? sessionId = null)
    {
        try
        {
            var requestMessage = new ApiChatMessage
            {
                Content = content,
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

    public async Task<List<Message>> GetConversationHistoryAsync(string sessionId)
    {
        try
        {
            var response = await _httpClient.GetAsync($"/api/chat/history/{sessionId}");
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

    public async Task EditMessageAsync(string sessionId, int messageIndex, string newContent)
    {
        // APIの仕様に編集機能がないため、削除して新しいメッセージを送信する
        // この実装は簡易的なもので、実際のAPIが編集機能を提供する場合はその仕様に従って実装する
        _logger.LogWarning("メッセージの編集は現在のAPIでは直接サポートされていません");
        await Task.CompletedTask;
    }

    public async Task DeleteMessageAsync(string sessionId, int messageNo)
    {
        try
        {
            var response = await _httpClient.DeleteAsync($"/api/chat/message/{sessionId}/{messageNo}");
            response.EnsureSuccessStatusCode();
        }
        catch (HttpRequestException ex)
        {
            _logger.LogError(ex, "API通信エラー: {Message}", ex.Message);
            throw new InvalidOperationException($"API通信エラー: {ex.Message}", ex);
        }
    }

    public async Task DeleteAllMessagesAsync(string sessionId)
    {
        try
        {
            var response = await _httpClient.DeleteAsync($"/api/chat/messages/{sessionId}");
            response.EnsureSuccessStatusCode();
        }
        catch (HttpRequestException ex)
        {
            _logger.LogError(ex, "API通信エラー: {Message}", ex.Message);
            throw new InvalidOperationException($"API通信エラー: {ex.Message}", ex);
        }
    }
} 