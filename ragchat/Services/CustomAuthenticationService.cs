using System.Security.Claims;
using System.Text.Json;
using Microsoft.JSInterop;

namespace ragchat.Services;

public class CustomAuthenticationService
{
    public event Action<ClaimsPrincipal>? UserChanged;
    private ClaimsPrincipal? currentUser;
    private IJSRuntime? jsRuntime;
    private bool initialized = false;

    public void SetJSRuntime(IJSRuntime jsRuntime)
    {
        this.jsRuntime = jsRuntime;
    }

    public ClaimsPrincipal CurrentUser
    {
        get { return currentUser ?? new(); }
        set
        {
            currentUser = value;
            _ = SaveUserToStorageAsync(value);

            if (UserChanged is not null)
            {
                UserChanged(currentUser);
            }
        }
    }

    public async Task InitializeAsync(IJSRuntime? jsRuntime = null)
    {
        if (jsRuntime != null)
        {
            this.jsRuntime = jsRuntime;
        }

        if (this.jsRuntime != null && !initialized)
        {
            try
            {
                var userJson = await this.jsRuntime.InvokeAsync<string>("localStorage.getItem", "currentUser");
                if (!string.IsNullOrEmpty(userJson))
                {
                    var userInfo = JsonSerializer.Deserialize<UserInfo>(userJson);
                    if (userInfo != null && !string.IsNullOrEmpty(userInfo.Name))
                    {
                        var identity = new ClaimsIdentity(
                            [new Claim(ClaimTypes.Name, userInfo.Name)],
                            "Custom Authentication");
                        currentUser = new ClaimsPrincipal(identity);
                    }
                }
                initialized = true;
            }
            catch
            {
                // ローカルストレージからの読み込みに失敗した場合は無視
            }
        }
    }

    private async Task SaveUserToStorageAsync(ClaimsPrincipal user)
    {
        if (jsRuntime != null)
        {
            try
            {
                if (user.Identity?.IsAuthenticated == true)
                {
                    var userInfo = new UserInfo { Name = user.Identity.Name ?? "" };
                    var userJson = JsonSerializer.Serialize(userInfo);
                    await jsRuntime.InvokeVoidAsync("localStorage.setItem", "currentUser", userJson);
                }
                else
                {
                    await jsRuntime.InvokeVoidAsync("localStorage.removeItem", "currentUser");
                }
            }
            catch
            {
                // ローカルストレージへの保存に失敗した場合は無視
            }
        }
    }

    public async Task SignOutAsync()
    {
        currentUser = new ClaimsPrincipal();
        if (jsRuntime != null)
        {
            try
            {
                await jsRuntime.InvokeVoidAsync("localStorage.removeItem", "currentUser");
            }
            catch
            {
                // ローカルストレージからの削除に失敗した場合は無視
            }
        }

        if (UserChanged is not null)
        {
            UserChanged(currentUser);
        }
    }

    private class UserInfo
    {
        public string Name { get; set; } = string.Empty;
    }
}