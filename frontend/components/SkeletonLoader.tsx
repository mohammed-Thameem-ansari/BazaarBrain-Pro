'use client';

import { motion } from 'framer-motion';

interface SkeletonProps {
  className?: string;
  height?: string;
  width?: string;
  rounded?: string;
}

const Skeleton = ({ className = '', height = 'h-4', width = 'w-full', rounded = 'rounded' }: SkeletonProps) => (
  <motion.div
    className={`bg-gray-200 ${height} ${width} ${rounded} ${className}`}
    animate={{
      opacity: [0.5, 1, 0.5],
    }}
    transition={{
      duration: 1.5,
      repeat: Infinity,
      ease: 'easeInOut',
    }}
  />
);

export const SkeletonText = ({ lines = 3, className = '' }: { lines?: number; className?: string }) => (
  <div className={`space-y-2 ${className}`}>
    {Array.from({ length: lines }).map((_, i) => (
      <Skeleton
        key={i}
        height="h-4"
        width={i === lines - 1 ? 'w-3/4' : 'w-full'}
        className="last:w-3/4"
      />
    ))}
  </div>
);

export const SkeletonCard = ({ className = '' }: { className?: string }) => (
  <div className={`bg-white rounded-lg border border-gray-200 p-6 ${className}`}>
    <div className="flex items-center space-x-4 mb-4">
      <Skeleton height="h-12" width="w-12" rounded="rounded-full" />
      <div className="flex-1">
        <Skeleton height="h-4" width="w-3/4" className="mb-2" />
        <Skeleton height="h-3" width="w-1/2" />
      </div>
    </div>
    <SkeletonText lines={3} />
  </div>
);

export const SkeletonTable = ({ rows = 5, columns = 4, className = '' }: { rows?: number; columns?: number; className?: string }) => (
  <div className={`bg-white rounded-lg border border-gray-200 overflow-hidden ${className}`}>
    {/* Header */}
    <div className="px-6 py-4 border-b border-gray-200">
      <div className="flex space-x-4">
        {Array.from({ length: columns }).map((_, i) => (
          <Skeleton key={i} height="h-4" width="w-20" />
        ))}
      </div>
    </div>
    
    {/* Rows */}
    <div className="divide-y divide-gray-200">
      {Array.from({ length: rows }).map((_, rowIndex) => (
        <div key={rowIndex} className="px-6 py-4">
          <div className="flex space-x-4">
            {Array.from({ length: columns }).map((_, colIndex) => (
              <Skeleton key={colIndex} height="h-4" width="w-20" />
            ))}
          </div>
        </div>
      ))}
    </div>
  </div>
);

export const SkeletonChart = ({ className = '' }: { className?: string }) => (
  <div className={`bg-white rounded-lg border border-gray-200 p-6 ${className}`}>
    <div className="flex items-center justify-between mb-6">
      <Skeleton height="h-6" width="w-32" />
      <Skeleton height="h-4" width="w-24" />
    </div>
    
    <div className="space-y-3">
      {Array.from({ length: 5 }).map((_, i) => (
        <div key={i} className="flex items-center space-x-4">
          <Skeleton height="h-4" width="w-20" />
          <div className="flex-1">
            <Skeleton height="h-3" width={`w-${Math.floor(Math.random() * 8 + 2)}/12`} />
          </div>
          <Skeleton height="h-4" width="w-16" />
        </div>
      ))}
    </div>
  </div>
);

export const SkeletonForm = ({ fields = 4, className = '' }: { fields?: number; className?: string }) => (
  <div className={`bg-white rounded-lg border border-gray-200 p-6 ${className}`}>
    <div className="space-y-6">
      {Array.from({ length: fields }).map((_, i) => (
        <div key={i}>
          <Skeleton height="h-4" width="w-24" className="mb-2" />
          <Skeleton height="h-10" width="w-full" />
        </div>
      ))}
      
      <div className="flex space-x-3 pt-4">
        <Skeleton height="h-10" width="w-24" />
        <Skeleton height="h-10" width="w-24" />
      </div>
    </div>
  </div>
);

export const SkeletonGrid = ({ items = 6, className = '' }: { items?: number; className?: string }) => (
  <div className={`grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 ${className}`}>
    {Array.from({ length: items }).map((_, i) => (
      <SkeletonCard key={i} />
    ))}
  </div>
);

export default Skeleton;
