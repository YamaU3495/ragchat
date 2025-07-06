using ragchat.Components;
using ragchat.Services;
using MudBlazor.Services;

var builder = WebApplication.CreateBuilder(args);

// Add services to the container.
builder.Services.AddRazorComponents()
    .AddInteractiveServerComponents();

// Add MudBlazor services
builder.Services.AddMudServices();

// Add HTTP client for API calls
builder.Services.AddHttpClient();

// ChatServiceの切り替え
var chatServiceType = builder.Configuration["ChatService:Type"] ?? "Api";
if (chatServiceType == "InMemory")
{
    builder.Services.AddSingleton<IChatService, InMemoryChatService>();
}
else
{
    builder.Services.AddScoped<IChatService, ChatService>();
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
