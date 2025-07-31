export function init(element, dotNetReference) {
    if (!element) return;

    // Store reference for cleanup
    element._dotNetReference = dotNetReference;
    element._isComposing = false; // IME入力状態を追跡
    
    // Set initial height
    resize(element);
    
    // IME入力状態の管理
    element.addEventListener('compositionstart', () => {
        element._isComposing = true;
    });
    
    element.addEventListener('compositionend', () => {
        element._isComposing = false;
        // IME入力完了時のみBlazorに通知
        if (dotNetReference) {
            dotNetReference.invokeMethodAsync('OnValueChanged', element.value);
        }
    });
    
    // Add input event listener for real-time resizing
    element.addEventListener('input', () => {
        resize(element);
        // IME入力中でない場合のみBlazorに通知
        if (!element._isComposing && dotNetReference) {
            dotNetReference.invokeMethodAsync('OnValueChanged', element.value);
        }
    });

    // キーボードイベント処理をJavaScript側で行う
    element.addEventListener('keydown', (e) => {
        if (dotNetReference) {
            // Enter + Shift でない場合（送信）
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault(); // デフォルトの改行を防ぐ
                dotNetReference.invokeMethodAsync('OnEnterPressedFromJS', element.value);
                return;
            }
            // その他のキーイベントもBlazorに通知
            dotNetReference.invokeMethodAsync('OnKeyDownFromJS', {
                key: e.key,
                shiftKey: e.shiftKey,
                ctrlKey: e.ctrlKey,
                altKey: e.altKey
            });
        }
    });

    // Handle paste events
    element.addEventListener('paste', () => {
        setTimeout(() => {
            resize(element);
            // ペースト後はIME入力中でないのでBlazorに通知
            if (dotNetReference) {
                dotNetReference.invokeMethodAsync('OnValueChanged', element.value);
            }
        }, 10);
    });
}

export function setValue(element, value) {
    if (element) {
        element.value = value || '';
        resize(element);
    }
}

export function getValue(element) {
    return element ? element.value : '';
}

export function resize(element) {
    if (!element) return;

    // Reset height to auto to get the scroll height
    element.style.height = 'auto';
    
    // Get the scroll height (content height)
    const scrollHeight = element.scrollHeight;
    
    // Get computed styles to check min/max height
    const computedStyle = window.getComputedStyle(element);
    const minHeight = parseInt(computedStyle.minHeight) || 40;
    const maxHeight = parseInt(computedStyle.maxHeight) || 200;
    
    // Calculate new height within bounds
    let newHeight = Math.max(minHeight, Math.min(scrollHeight, maxHeight));
    
    // Set the height
    element.style.height = newHeight + 'px';
    
    // Show scrollbar only if content exceeds max height
    if (scrollHeight > maxHeight) {
        element.style.overflowY = 'auto';
    } else {
        element.style.overflowY = 'hidden';
    }
}

export function focus(element) {
    if (element) {
        element.focus();
    }
}

export function clear(element) {
    if (element) {
        element.value = '';
        resize(element);
    }
}

export function dispose(element) {
    if (element && element._dotNetReference) {
        element._dotNetReference.dispose();
        element._dotNetReference = null;
    }
} 