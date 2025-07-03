import React from 'react';
import { AiOutlineLoading3Quarters } from 'react-icons/ai';

const sizeMap = {
  sm: 'w-6 h-6',
  md: 'w-8 h-8',
  lg: 'w-12 h-12',
};

const LoadingSpinner = ({ size = 'md', color = 'text-indigo-600' }) => {
  const sizeClass = sizeMap[size] || sizeMap.md;
  const colorClass = color;
  const classNames = `${sizeClass} ${colorClass} animate-spin`;

  return (
    <div className="flex items-center justify-center">
      <AiOutlineLoading3Quarters className={classNames} role="status" aria-live="polite" aria-label="Loading..." />
    </div>
  );
};

export default LoadingSpinner;
