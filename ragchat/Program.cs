using ragchat.Components;
using ragchat.Services;
using MudBlazor.Services;
using Microsoft.IdentityModel.Protocols.OpenIdConnect;
using Microsoft.AspNetCore.Authentication.OpenIdConnect;
using Microsoft.AspNetCore.Authentication.Cookies;
using BlazorWebAppOidc;
using Microsoft.AspNetCore.HttpOverrides; // ← 追加

const string KEYCLOAK_OIDC_SCHEME = "KeycloakOidc";
var builder = WebApplication.CreateBuilder(args);

// Forwarded Headers設定を追加
builder.Services.Configure<ForwardedHeadersOptions>(options =>
{
    options.ForwardedHeaders = ForwardedHeaders.XForwardedFor | ForwardedHeaders.XForwardedProto;
    options.KnownNetworks.Clear();
    options.KnownProxies.Clear();
});

// Add services to the container.
builder.Services.AddAuthentication(KEYCLOAK_OIDC_SCHEME)
    .AddOpenIdConnect(KEYCLOAK_OIDC_SCHEME, oidcOptions =>
    {
        // For the following OIDC settings, any line that's commented out
        // represents a DEFAULT setting. If you adopt the default, you can
        // remove the line if you wish.

        // ........................................................................
        // Pushed Authorization Requests (PAR) support. By default, the setting is
        // to use PAR if the identity provider's discovery document (usually found 
        // at '.well-known/openid-configuration') advertises support for PAR. If 
        // you wish to require PAR support for the app, you can assign 
        // 'PushedAuthorizationBehavior.Require' to 'PushedAuthorizationBehavior'.
        //
        // Note that PAR isn't supported by Microsoft Entra, and there are no plans
        // for Entra to ever support it in the future.

        oidcOptions.PushedAuthorizationBehavior = PushedAuthorizationBehavior.Disable;
        // ........................................................................

        // ........................................................................
        // The OIDC handler must use a sign-in scheme capable of persisting 
        // user credentials across requests.

        oidcOptions.SignInScheme = CookieAuthenticationDefaults.AuthenticationScheme;
        // ........................................................................

        // ........................................................................
        // The "openid" and "profile" scopes are required for the OIDC handler 
        // and included by default. You should enable these scopes here if scopes 
        // are provided by "Authentication:Schemes:MicrosoftOidc:Scope" 
        // configuration because configuration may overwrite the scopes collection.

        //oidcOptions.Scope.Add(OpenIdConnectScope.OpenIdProfile);
        // ........................................................................

        // ........................................................................
        // The "Weather.Get" scope for accessing the external web API for weather
        // data. The following example is based on using Microsoft Entra ID in 
        // an ME-ID tenant domain (the {APP ID URI} placeholder is found in
        // the Entra or Azure portal where the web API is exposed). For any other
        // identity provider, use the appropriate scope.

        // oidcOptions.Scope.Add("Weather.Get");
        oidcOptions.Scope.Add("Message.Get");
        // ........................................................................

        // ........................................................................
        // 以下のパスは、OIDCプロバイダーにアプリケーションを登録する際に設定した
        // リダイレクトパスとログアウト後のリダイレクトパスと一致する必要があります。
        // デフォルト値は "/signin-oidc" と "/signout-callback-oidc" です。

        oidcOptions.CallbackPath = new PathString("/signin-oidc");
        oidcOptions.SignedOutCallbackPath = new PathString("/signout-callback-oidc");
        // ........................................................................

        // ........................................................................
        // The RemoteSignOutPath is the "Front-channel logout URL" for remote single 
        // sign-out. The default value is "/signout-oidc".

        oidcOptions.RemoteSignOutPath = new PathString("/signout-oidc");
        // ........................................................................

        // ........................................................................
        // The following example Authority is configured for Microsoft Entra ID
        // and a single-tenant application registration. Set the {TENANT ID} 
        // placeholder to the Tenant ID. The "common" Authority 
        // https://login.microsoftonline.com/common/v2.0/ should be used 
        // for multi-tenant apps. You can also use the "common" Authority for 
        // single-tenant apps, but it requires a custom IssuerValidator as shown 
        // in the comments below. 

        oidcOptions.Authority = builder.Configuration["Authentication:Schemes:KeycloakOidc:Authority"] ?? "http://localhost:8080/realms/ragchat";
        // ........................................................................

        // ........................................................................
        // Set the Client ID for the app. Set the {CLIENT ID} placeholder to
        // the Client ID.

        oidcOptions.ClientId = "ragchat";
        // ........................................................................

        // ........................................................................
        // Set the Client Secret for the app. This should be configured via
        // environment variable Authentication__Schemes__KeycloakOidc__ClientSecret

        // oidcOptions.ClientSecret = builder.Configuration["Authentication:Schemes:KeycloakOidc:ClientSecret"];
        oidcOptions.ClientSecret = "WM4KSAy7Q9YMlF8lBsgOzIHoRadyUXk5";
        // ........................................................................

        // ........................................................................
        // Setting ResponseType to "code" configures the OIDC handler to use 
        // authorization code flow. Implicit grants and hybrid flows are unnecessary
        // in this mode. In a Microsoft Entra ID app registration, you don't need to 
        // select either box for the authorization endpoint to return access tokens 
        // or ID tokens. The OIDC handler automatically requests the appropriate 
        // tokens using the code returned from the authorization endpoint.

        oidcOptions.ResponseType = OpenIdConnectResponseType.Code;
        // ........................................................................

        // ........................................................................
        // Set MapInboundClaims to "false" to obtain the original claim types from 
        // the token. Many OIDC servers use "name" and "role"/"roles" rather than 
        // the SOAP/WS-Fed defaults in ClaimTypes. Adjust these values if your 
        // identity provider uses different claim types.

        oidcOptions.MapInboundClaims = false;
        oidcOptions.TokenValidationParameters.NameClaimType = "name";
        oidcOptions.TokenValidationParameters.RoleClaimType = "role";
        // oidcOptions.TokenValidationParameters.RoleClaimType = "roles";
        // ........................................................................

        // ........................................................................
        // Many OIDC providers work with the default issuer validator, but the
        // configuration must account for the issuer parameterized with "{TENANT ID}" 
        // returned by the "common" endpoint's /.well-known/openid-configuration
        // For more information, see
        // https://github.com/AzureAD/azure-activedirectory-identitymodel-extensions-for-dotnet/issues/1731

        //var microsoftIssuerValidator = AadIssuerValidator.GetAadIssuerValidator(oidcOptions.Authority);
        //oidcOptions.TokenValidationParameters.IssuerValidator = microsoftIssuerValidator.Validate;
        // ........................................................................

        // ........................................................................
        // OIDC connect options set later via ConfigureCookieOidc
        //
        // (1) The "offline_access" scope is required for the refresh token.
        //
        // (2) SaveTokens is set to true, which saves the access and refresh tokens
        // in the cookie, so the app can authenticate requests for weather data and
        // use the refresh token to obtain a new access token on access token
        // expiration.
        // ........................................................................
        
        // 開発環境用の設定(HTTPでも通信可能にするため)
        oidcOptions.RequireHttpsMetadata = false;

        // 証明書の検証を行わない
        var handler = new HttpClientHandler();
        handler.ServerCertificateCustomValidationCallback = (message, cert, chain, sslPolicyErrors) => true;
        oidcOptions.BackchannelHttpHandler = handler;
    })
    .AddCookie(CookieAuthenticationDefaults.AuthenticationScheme);
builder.Services.ConfigureCookieOidc(CookieAuthenticationDefaults.AuthenticationScheme, KEYCLOAK_OIDC_SCHEME);

builder.Services.AddAuthorization();

builder.Services.AddCascadingAuthenticationState();

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

// SessionServiceの切り替え
var sessionServiceType = builder.Configuration["SessionService:Type"] ?? "Cookie";
if (sessionServiceType == "InMemory")
{   
    Console.WriteLine("SessionService: InMemory");
    builder.Services.AddSingleton<ISessionService, InMemorySessionService>();
}
else if (sessionServiceType == "Api")
{
    Console.WriteLine("SessionService: Api");
    builder.Services.AddScoped<ISessionService, ApiSessionService>();
}
else
{
    Console.WriteLine("SessionService: Cookie");
    builder.Services.AddScoped<ISessionService, CookieSessionService>();
}

var app = builder.Build();

app.UseForwardedHeaders();

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

app.MapGroup("/authentication").MapLoginAndLogout();

app.Run();
