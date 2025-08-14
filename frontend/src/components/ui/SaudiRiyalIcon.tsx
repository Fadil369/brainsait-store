'use client';

import React from 'react';

interface SaudiRiyalIconProps {
  size?: number;
  className?: string;
  color?: string;
}

/**
 * New Saudi Riyal Symbol Component (2025)
 * Based on the official SAMA design with geometric Arabic calligraphy
 */
export const SaudiRiyalIcon: React.FC<SaudiRiyalIconProps> = ({ 
  size = 24, 
  className = '', 
  color = 'currentColor' 
}) => {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 100 100"
      className={className}
      xmlns="http://www.w3.org/2000/svg"
    >
      <g transform="translate(50,50)">
        {/* Main vertical strokes - representing ر (Ra) and ل (Lam) */}
        <path
          d="M -15 -30 L -15 -10 L -8 -10 L -8 30 L -15 30 L -15 35 L 8 35 L 8 30 L 0 30 L 0 -10 L 15 -10 L 15 -30 Z"
          fill={color}
          stroke="none"
        />
        
        {/* Horizontal connecting strokes - representing ي (Ya) connections */}
        <path
          d="M -25 -5 L -15 -5 L -15 0 L -25 0 Z"
          fill={color}
          stroke="none"
        />
        
        <path
          d="M -25 10 L -8 10 L -8 15 L -25 15 Z"
          fill={color}
          stroke="none"
        />
        
        <path
          d="M 15 5 L 30 5 L 30 10 L 15 10 Z"
          fill={color}
          stroke="none"
        />
        
        {/* Modern geometric accent - representing the stylized calligraphy */}
        <path
          d="M 15 20 L 25 20 L 25 25 L 15 25 Z"
          fill={color}
          stroke="none"
        />
      </g>
    </svg>
  );
};

/**
 * Simplified inline SAR symbol for text usage
 */
export const SARSymbol: React.FC<{ size?: number; className?: string }> = ({ 
  size = 16, 
  className = '' 
}) => {
  return (
    <span className={`inline-flex items-center ${className}`} style={{ fontSize: size }}>
      <SaudiRiyalIcon size={size} />
    </span>
  );
};

export default SaudiRiyalIcon;