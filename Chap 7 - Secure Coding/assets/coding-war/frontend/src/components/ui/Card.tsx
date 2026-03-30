import { type ReactNode } from 'react';

export interface CardProps {
  children: ReactNode;
  className?: string;
  padding?: 'none' | 'sm' | 'md' | 'lg';
  hover?: boolean;
  onClick?: () => void;
}

export default function Card({ children, className = '', padding = 'md', hover = false, onClick }: CardProps) {
  const baseStyles = 'bg-white dark:bg-gray-800 rounded-lg shadow-md';
  
  const paddingStyles = {
    none: '',
    sm: 'p-4',
    md: 'p-6',
    lg: 'p-8',
  };
  
  const hoverStyles = hover ? 'transition-shadow hover:shadow-lg cursor-pointer' : '';
  
  return (
    <div 
      className={`${baseStyles} ${paddingStyles[padding]} ${hoverStyles} ${className}`}
      onClick={onClick}
    >
      {children}
    </div>
  );
}
