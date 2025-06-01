import React from 'react';

type ButtonProps = React.TextareaHTMLAttributes<HTMLButtonElement> & {
  children: React.ReactNode;
  onClick?: (e?: React.UIEvent) => void;
  type?: 'button' | 'submit' | 'reset';
  className?: string;
};

const Button: React.FC<ButtonProps> = ({ children, onClick, type = 'button', className, style }) => (
  <button type={type} onClick={onClick} className={className} style={style}>
    {children}
  </button>
);

export default Button; 