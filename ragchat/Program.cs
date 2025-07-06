using ragchat.Components;
using ragchat.Services;
using MudBlazor.Services;

var builder = WebApplication.CreateBuilder(args);

// Add services to the container.
builder.Services.AddRazorComponents()
    .AddInteractiveServerComponents();

// Add MudBlazor services
builder.Services.AddMudServices();

// Add HTTP client factory for API calls
builder.Services.AddHttpClient();

// Configure named HttpClient for API calls
builder.Services.AddHttpClient("ApiClient", client =>
{
    var apiConfig = builder.Configuration.GetSection("Api");
    var protocol = apiConfig["Protocol"] ?? "http";
    var host = apiConfig["Host"] ?? "localhost";
    var port = apiConfig["Port"] ?? "8000";
    var baseUrl = $"{protocol}://{host}:{port}";
    
    client.BaseAddress = new Uri(baseUrl);
    client.DefaultRequestHeaders.Add("User-Agent", "RagChat/1.0");
    client.Timeout = TimeSpan.FromSeconds(30);
});

// ChatServiceの切り替え
var chatServiceType = builder.Configuration["ChatService:Type"] ?? "Api";
if (chatServiceType == "InMemory")
{   
    Console.WriteLine("ChatService: InMemory");
    builder.Services.AddSingleton<IChatService, InMemoryChatService>();
}
else
{
    Console.WriteLine("ChatService: Api");
    builder.Services.AddScoped<IChatService, ApiChatService>();
}

var app = builder.Build();

// Configure the HTTP request pipeline.
if (!app.Environment.IsDevelopment())
{
    app.UseExceptionHandler("/Error", createScopeForErrors: true);
    // The default HSTS value is 30 days. You may want to change this for production scenarios, see https://aka.ms/aspnetcore-hsts.
    app.UseHsts();
}

app.UseHttpsRedirection();

app.UseStaticFiles();
app.UseAntiforgery();

app.MapRazorComponents<App>()
    .AddInteractiveServerRenderMode();

app.Run();
