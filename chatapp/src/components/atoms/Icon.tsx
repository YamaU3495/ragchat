import React from 'react';

type IconProps = {
  name: 'send' | 'menu' | 'edit';
  size?: number;
  color?: string;
  className?: string;
};

const Icon: React.FC<IconProps> = ({ name, size = 24, color = '#333', className }) => {
  switch (name) {
    case 'send':
      return (
        <svg
          width={size}
          height={size}
          viewBox="0 0 24 24"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
          className={className}
        >
          <path d="M2 21L23 12L2 3V10L17 12L2 14V21Z" fill={color} />
        </svg>
      );
    case 'menu':
      return (
        <svg
          width={size}
          height={size}
          viewBox="0 0 24 24"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
          className={className}
        >
          <rect x="3" y="6" width="18" height="2" rx="1" fill={color} />
          <rect x="3" y="11" width="18" height="2" rx="1" fill={color} />
          <rect x="3" y="16" width="18" height="2" rx="1" fill={color} />
        </svg>
      );
    case 'edit':
      return (
        <svg
          width={size}
          height={size}
          viewBox="0 0 24 24"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
          className={className}
        >
          <path d="M3 17.25V21h3.75l11.06-11.06-3.75-3.75L3 17.25zM20.71 7.04a1.003 1.003 0 0 0 0-1.42l-2.34-2.34a1.003 1.003 0 0 0-1.42 0l-1.83 1.83 3.75 3.75 1.84-1.82z" fill={color} />
        </svg>
      );
    default:
      return null;
  }
};

export default Icon; 