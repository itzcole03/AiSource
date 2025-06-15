import React from 'react';

interface LoadingSkeletonProps {
  className?: string;
  variant?: 'card' | 'text' | 'circle' | 'button';
  lines?: number;
}

export const LoadingSkeleton: React.FC<LoadingSkeletonProps> = ({ 
  className = '', 
  variant = 'text',
  lines = 1 
}) => {
  const baseClasses = 'animate-pulse bg-gray-200 rounded';
  
  if (variant === 'card') {
    return (
      <div className={`bg-white rounded-xl shadow-sm border border-gray-200 p-6 ${className}`}>
        <div className="animate-pulse">
          <div className="flex items-center space-x-3 mb-4">
            <div className="w-12 h-12 bg-gray-200 rounded-lg"></div>
            <div className="flex-1">
              <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
              <div className="h-3 bg-gray-200 rounded w-1/2"></div>
            </div>
          </div>
          <div className="space-y-3">
            <div className="h-3 bg-gray-200 rounded"></div>
            <div className="h-3 bg-gray-200 rounded w-5/6"></div>
            <div className="h-3 bg-gray-200 rounded w-4/6"></div>
          </div>
        </div>
      </div>
    );
  }

  if (variant === 'circle') {
    return <div className={`${baseClasses} rounded-full ${className}`}></div>;
  }

  if (variant === 'button') {
    return <div className={`${baseClasses} h-10 w-24 ${className}`}></div>;
  }

  return (
    <div className={className}>
      {Array.from({ length: lines }).map((_, index) => (
        <div
          key={index}
          className={`${baseClasses} h-4 ${index === lines - 1 ? 'w-3/4' : 'w-full'} ${
            index > 0 ? 'mt-2' : ''
          }`}
        ></div>
      ))}
    </div>
  );
};

export const ProviderCardSkeleton: React.FC = () => (
  <LoadingSkeleton variant="card" className="mb-6" />
);

export const SystemMonitorSkeleton: React.FC = () => (
  <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
    <div className="animate-pulse">
      <div className="flex items-center space-x-2 mb-6">
        <LoadingSkeleton variant="circle" className="w-5 h-5" />
        <div className="h-5 bg-gray-200 rounded w-32"></div>
      </div>
      
      <div className="space-y-6">
        {[1, 2, 3].map((i) => (
          <div key={i}>
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center space-x-2">
                <LoadingSkeleton variant="circle" className="w-4 h-4" />
                <div className="h-4 bg-gray-200 rounded w-12"></div>
              </div>
              <div className="h-4 bg-gray-200 rounded w-8"></div>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2"></div>
            <div className="h-3 bg-gray-200 rounded w-16 mt-1"></div>
          </div>
        ))}
      </div>
    </div>
  </div>
);