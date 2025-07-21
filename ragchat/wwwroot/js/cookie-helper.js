window.cookieHelper = {
    setCookie: function (name, value, days) {
        console.log('setCookie called:', { name, value, days });
        let expires = "";
        if (days) {
            const date = new Date();
            date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
            expires = "; expires=" + date.toUTCString();
        }
        const cookieString = name + "=" + (value || "") + expires + "; path=/";
        console.log('Setting cookie:', cookieString);
        document.cookie = cookieString;
        
        // 設定後に確認
        const verification = this.getCookie(name);
        console.log('Cookie verification after set:', verification);
    },

    getCookie: function (name) {
        console.log('getCookie called for:', name);
        const nameEQ = name + "=";
        const ca = document.cookie.split(';');
        console.log('All cookies:', document.cookie);
        for (let i = 0; i < ca.length; i++) {
            let c = ca[i];
            while (c.charAt(0) === ' ') c = c.substring(1, c.length);
            if (c.indexOf(nameEQ) === 0) {
                const result = c.substring(nameEQ.length, c.length);
                console.log('Found cookie value:', result);
                return result;
            }
        }
        console.log('Cookie not found');
        return null;
    },

    deleteCookie: function (name) {
        console.log('deleteCookie called for:', name);
        document.cookie = name + "=; Path=/; Expires=Thu, 01 Jan 1970 00:00:01 GMT;";
    }
};

// ログアウトフォーム送信ヘルパー
window.submitLogoutForm = function(returnUrl) {
    const form = document.createElement("form");
    form.method = "post";
    form.action = "authentication/logout";
    
    const antiforgeryToken = document.createElement("input");
    antiforgeryToken.type = "hidden";
    antiforgeryToken.name = "__RequestVerificationToken";
    const existingToken = document.querySelector('input[name="__RequestVerificationToken"]');
    antiforgeryToken.value = existingToken ? existingToken.value : '';
    
    const returnUrlInput = document.createElement("input");
    returnUrlInput.type = "hidden";
    returnUrlInput.name = "ReturnUrl";
    returnUrlInput.value = returnUrl;
    
    form.appendChild(antiforgeryToken);
    form.appendChild(returnUrlInput);
    document.body.appendChild(form);
    form.submit();
};

// メニュー外クリック検知ヘルパー
window.addClickOutsideListener = function(element, dotNetHelper) {
    document.addEventListener('click', function(event) {
        if (!element.contains(event.target)) {
            dotNetHelper.invokeMethodAsync('OnClickOutside');
        }
    });
}; 