using Microsoft.AspNetCore.Components.Authorization;
using Microsoft.JSInterop;
using System.Security.Claims;

namespace ragchat.Services;

public class CustomAuthStateProvider : AuthenticationStateProvider
{
    private AuthenticationState authenticationState;
    private readonly CustomAuthenticationService authService;
    private readonly IJSRuntime jsRuntime;
    private bool initialized = false;

    public CustomAuthStateProvider(CustomAuthenticationService service, IJSRuntime jsRuntime)
    {
        authService = service;
        this.jsRuntime = jsRuntime;
        authenticationState = new AuthenticationState(service.CurrentUser);

        service.UserChanged += (newUser) =>
        {
            authenticationState = new AuthenticationState(newUser);
            NotifyAuthenticationStateChanged(Task.FromResult(authenticationState));
        };
    }

    public override async Task<AuthenticationState> GetAuthenticationStateAsync()
    {
        if (!initialized)
        {
            await authService.InitializeAsync(jsRuntime);
            authenticationState = new AuthenticationState(authService.CurrentUser);
            initialized = true;
        }
        return authenticationState;
    }
}