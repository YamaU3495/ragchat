using Microsoft.AspNetCore.Authentication;
using Microsoft.AspNetCore.Authentication.Cookies;
using Microsoft.AspNetCore.Authentication.OpenIdConnect;
using Microsoft.AspNetCore.Mvc;

namespace Microsoft.AspNetCore.Routing;

internal static class LoginLogoutEndpointRouteBuilderExtensions
{
    internal static IEndpointConventionBuilder MapLoginAndLogout(this IEndpointRouteBuilder endpoints)
    {
        var group = endpoints.MapGroup("");

        group.MapGet("/login", (string? returnUrl) => TypedResults.Challenge(GetAuthProperties(returnUrl)))
            .AllowAnonymous();

        // Sign out of the Cookie and OIDC handlers. If you do not sign out with the OIDC handler,
        // the user will automatically be signed back in the next time they visit a page that requires authentication
        // without being able to choose another account.
        group.MapPost("/logout", async (HttpContext context, [FromForm] string? returnUrl) =>
        {
            try
            {
                // セッション期限切れエラーを無視してログアウト処理を実行
                await context.SignOutAsync(CookieAuthenticationDefaults.AuthenticationScheme);
                await context.SignOutAsync("KeycloakOidc", GetAuthProperties(returnUrl));
                
                // ログアウト成功時はリダイレクト
                context.Response.Redirect(returnUrl ?? "/");
            }
            catch (Exception ex)
            {
                // セッション期限切れなどのエラーが発生した場合でもログアウト処理を継続
                // ログに記録（本番環境では適切なログレベルに設定）
                Console.WriteLine($"Logout error (ignored): {ex.Message}");
                
                // エラーが発生してもログアウト処理を完了
                context.Response.Redirect(returnUrl ?? "/");
            }
        });

        return group;
    }

    private static AuthenticationProperties GetAuthProperties(string? returnUrl)
    {
        // TODO: Use HttpContext.Request.PathBase instead.
        const string pathBase = "/";

        // Prevent open redirects.
        if (string.IsNullOrEmpty(returnUrl))
        {
            returnUrl = pathBase;
        }
        else if (!Uri.IsWellFormedUriString(returnUrl, UriKind.Relative))
        {
            returnUrl = new Uri(returnUrl, UriKind.Absolute).PathAndQuery;
        }
        else if (returnUrl[0] != '/')
        {
            returnUrl = $"{pathBase}{returnUrl}";
        }

        return new AuthenticationProperties { RedirectUri = returnUrl };
    }
}
