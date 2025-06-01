import React from 'react';

type AvatarProps = {
  src: string;
  alt?: string;
  size?: number;
  className?: string;
};

const Avatar: React.FC<AvatarProps> = ({ src, alt = 'avatar', size = 40, className }) => (
  <img
    src={src}
    alt={alt}
    width={size}
    height={size}
    className={className}
    style={{ borderRadius: '50%', objectFit: 'cover' }}
  />
);

export default Avatar; 