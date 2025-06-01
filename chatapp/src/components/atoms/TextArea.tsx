import React, { forwardRef, useRef, useEffect } from 'react';

type TextAreaProps = React.TextareaHTMLAttributes<HTMLTextAreaElement> & {
  className?: string;
  backgroundColor?: string;
  autoResize?: boolean;
};

const TextArea = forwardRef<HTMLTextAreaElement, TextAreaProps>(
  ({ className, backgroundColor, style, autoResize, value, onInput, ...props }, ref) => {
    const innerRef = useRef<HTMLTextAreaElement>(null);
    const combinedRef = (ref as React.RefObject<HTMLTextAreaElement>) || innerRef;

    useEffect(() => {
      if (autoResize && combinedRef.current) {
        combinedRef.current.style.height = 'auto';
        combinedRef.current.style.height = combinedRef.current.scrollHeight + 'px';
      }
    }, [value, autoResize, combinedRef]);

    const handleInput = (e: React.FormEvent<HTMLTextAreaElement>) => {
      if (autoResize && combinedRef.current) {
        combinedRef.current.style.height = 'auto';
        combinedRef.current.style.height = combinedRef.current.scrollHeight + 'px';
      }
      if (onInput) onInput(e);
    };

    return (
      <textarea
        ref={combinedRef}
        className={className}
        style={{ ...style, backgroundColor }}
        value={value}
        onInput={handleInput}
        {...props}
      />
    );
  }
);

export default TextArea; 