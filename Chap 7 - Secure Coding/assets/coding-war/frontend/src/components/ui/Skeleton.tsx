import { type HTMLAttributes } from 'react';

export interface SkeletonProps extends HTMLAttributes<HTMLDivElement> {
  width?: string;
  height?: string;
  variant?: 'text' | 'circular' | 'rectangular';
  count?: number;
}

export default function Skeleton({ 
  width, 
  height, 
  variant = 'text', 
  count = 1, 
  className = '',
  ...props 
}: SkeletonProps) {
  const baseStyles = 'bg-gray-200 dark:bg-gray-700 animate-pulse';
  
  const variantStyles = {
    text: 'h-4 rounded',
    circular: 'rounded-full',
    rectangular: 'rounded-md',
  };

  const skeletonStyle = {
    width: width || (variant === 'circular' ? height : undefined),
    height: height,
  };

  if (count > 1) {
    return (
      <div className="space-y-3">
        {Array.from({ length: count }).map((_, index) => (
          <div
            key={index}
            className={`${baseStyles} ${variantStyles[variant]} ${className}`}
            style={skeletonStyle}
            {...props}
          />
        ))}
      </div>
    );
  }

  return (
    <div
      className={`${baseStyles} ${variantStyles[variant]} ${className}`}
      style={skeletonStyle}
      {...props}
    />
  );
}

// Preset skeleton components for common use cases

export function SkeletonText({ lines = 3, className = '' }: { lines?: number; className?: string }) {
  return (
    <div className={`space-y-3 ${className}`}>
      {Array.from({ length: lines }).map((_, index) => (
        <Skeleton
          key={index}
          width={index === lines - 1 ? '75%' : '100%'}
          variant="text"
        />
      ))}
    </div>
  );
}

export function SkeletonCard({ className = '' }: { className?: string }) {
  return (
    <div className={`bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 ${className}`}>
      <Skeleton width="50%" height="24px" className="mb-4" />
      <SkeletonText lines={2} />
    </div>
  );
}

export function SkeletonTable({ rows = 3, className = '' }: { rows?: number; className?: string }) {
  return (
    <div className={`space-y-3 ${className}`}>
      {Array.from({ length: rows }).map((_, index) => (
        <div key={index} className="flex space-x-4">
          <Skeleton width="25%" height="40px" />
          <Skeleton width="50%" height="40px" />
          <Skeleton width="25%" height="40px" />
        </div>
      ))}
    </div>
  );
}

export function SkeletonAvatar({ className = '' }: { className?: string }) {
  return (
    <div className={`flex items-center space-x-4 ${className}`}>
      <Skeleton variant="circular" width="48px" height="48px" />
      <div className="flex-1 space-y-2">
        <Skeleton width="33%" height="16px" />
        <Skeleton width="50%" height="12px" />
      </div>
    </div>
  );
}
