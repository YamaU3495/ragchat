export function init(element, dotNetReference) {
    if (!element) return;

    // Store reference for cleanup
    element._dotNetReference = dotNetReference;
    
    // Set initial height
    resize(element);
    
    // Add input event listener for real-time resizing
    element.addEventListener('input', () => {
        resize(element);
        // Notify Blazor component of value change
        if (dotNetReference) {
            dotNetReference.invokeMethodAsync('OnValueChanged', element.value);
        }
    });

    // Handle paste events
    element.addEventListener('paste', () => {
        setTimeout(() => {
            resize(element);
        }, 10);
    });
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