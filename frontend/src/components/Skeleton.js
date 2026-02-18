import React from 'react';
import { motion } from 'framer-motion';

// Base skeleton pulse animation
const pulseAnimation = {
  initial: { opacity: 0.4 },
  animate: { 
    opacity: [0.4, 0.7, 0.4],
    transition: {
      duration: 1.5,
      repeat: Infinity,
      ease: 'easeInOut',
    }
  }
};

// Skeleton line component
export const SkeletonLine = ({ className = '', width = '100%' }) => (
  <motion.div
    className={`h-4 bg-zinc-800 rounded ${className}`}
    style={{ width }}
    {...pulseAnimation}
  />
);

// Skeleton circle component
export const SkeletonCircle = ({ size = 40, className = '' }) => (
  <motion.div
    className={`rounded-full bg-zinc-800 ${className}`}
    style={{ width: size, height: size }}
    {...pulseAnimation}
  />
);

// Skeleton card component
export const SkeletonCard = ({ className = '' }) => (
  <motion.div
    className={`rounded-xl bg-zinc-900/50 border border-zinc-800 p-6 ${className}`}
    initial={{ opacity: 0 }}
    animate={{ opacity: 1 }}
    transition={{ duration: 0.3 }}
  >
    <div className="space-y-4">
      <motion.div className="h-5 bg-zinc-800 rounded w-1/3" {...pulseAnimation} />
      <motion.div className="h-8 bg-zinc-800 rounded w-2/3" {...pulseAnimation} />
      <motion.div className="h-4 bg-zinc-800 rounded w-full" {...pulseAnimation} />
    </div>
  </motion.div>
);

// Skeleton stat card
export const SkeletonStatCard = ({ className = '' }) => (
  <motion.div
    className={`rounded-xl bg-zinc-900/50 border border-zinc-800 p-5 ${className}`}
    initial={{ opacity: 0, y: 10 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ duration: 0.3 }}
  >
    <div className="flex items-start justify-between">
      <div className="space-y-3 flex-1">
        <motion.div className="h-3 bg-zinc-800 rounded w-24" {...pulseAnimation} />
        <motion.div className="h-7 bg-zinc-800 rounded w-20" {...pulseAnimation} />
        <motion.div className="h-3 bg-zinc-800 rounded w-16" {...pulseAnimation} />
      </div>
      <motion.div 
        className="w-12 h-12 bg-zinc-800 rounded-xl"
        {...pulseAnimation}
      />
    </div>
  </motion.div>
);

// Skeleton table
export const SkeletonTable = ({ rows = 5, cols = 4, className = '' }) => (
  <motion.div
    className={`rounded-xl bg-zinc-900/50 border border-zinc-800 overflow-hidden ${className}`}
    initial={{ opacity: 0 }}
    animate={{ opacity: 1 }}
  >
    {/* Header */}
    <div className="grid gap-4 p-4 bg-zinc-800/30 border-b border-zinc-800" style={{ gridTemplateColumns: `repeat(${cols}, 1fr)` }}>
      {[...Array(cols)].map((_, i) => (
        <motion.div key={i} className="h-4 bg-zinc-700 rounded" {...pulseAnimation} />
      ))}
    </div>
    {/* Rows */}
    {[...Array(rows)].map((_, rowIndex) => (
      <div 
        key={rowIndex} 
        className="grid gap-4 p-4 border-b border-zinc-800/50 last:border-b-0"
        style={{ gridTemplateColumns: `repeat(${cols}, 1fr)` }}
      >
        {[...Array(cols)].map((_, colIndex) => (
          <motion.div 
            key={colIndex} 
            className="h-4 bg-zinc-800 rounded"
            style={{ width: `${60 + Math.random() * 40}%` }}
            {...pulseAnimation}
          />
        ))}
      </div>
    ))}
  </motion.div>
);

// Skeleton chart
export const SkeletonChart = ({ className = '', height = 200 }) => (
  <motion.div
    className={`rounded-xl bg-zinc-900/50 border border-zinc-800 p-6 ${className}`}
    initial={{ opacity: 0 }}
    animate={{ opacity: 1 }}
  >
    <div className="flex justify-between items-center mb-6">
      <motion.div className="h-5 bg-zinc-800 rounded w-32" {...pulseAnimation} />
      <motion.div className="h-4 bg-zinc-800 rounded w-20" {...pulseAnimation} />
    </div>
    <div className="flex items-end gap-2" style={{ height }}>
      {[...Array(12)].map((_, i) => (
        <motion.div
          key={i}
          className="flex-1 bg-zinc-800 rounded-t"
          style={{ height: `${20 + Math.random() * 80}%` }}
          {...pulseAnimation}
        />
      ))}
    </div>
  </motion.div>
);

// Skeleton KPI strip
export const SkeletonKPIStrip = ({ count = 4, className = '' }) => (
  <div className={`grid grid-cols-2 md:grid-cols-4 gap-4 ${className}`}>
    {[...Array(count)].map((_, i) => (
      <SkeletonStatCard key={i} />
    ))}
  </div>
);

// Dashboard skeleton
export const DashboardSkeleton = () => (
  <div className="space-y-6 p-6">
    <SkeletonKPIStrip />
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <SkeletonChart height={250} />
      <SkeletonChart height={250} />
    </div>
    <SkeletonTable rows={5} cols={5} />
  </div>
);

// Page transition wrapper
export const PageTransition = ({ children, className = '' }) => (
  <motion.div
    className={className}
    initial={{ opacity: 0, y: 8 }}
    animate={{ opacity: 1, y: 0 }}
    exit={{ opacity: 0, y: -8 }}
    transition={{ duration: 0.2, ease: 'easeOut' }}
  >
    {children}
  </motion.div>
);

// Fade slide transition
export const FadeSlide = ({ children, direction = 'up', delay = 0 }) => {
  const variants = {
    up: { initial: { opacity: 0, y: 20 }, animate: { opacity: 1, y: 0 } },
    down: { initial: { opacity: 0, y: -20 }, animate: { opacity: 1, y: 0 } },
    left: { initial: { opacity: 0, x: 20 }, animate: { opacity: 1, x: 0 } },
    right: { initial: { opacity: 0, x: -20 }, animate: { opacity: 1, x: 0 } },
  };

  return (
    <motion.div
      initial={variants[direction].initial}
      animate={variants[direction].animate}
      transition={{ duration: 0.4, delay, ease: 'easeOut' }}
    >
      {children}
    </motion.div>
  );
};

export default {
  SkeletonLine,
  SkeletonCircle,
  SkeletonCard,
  SkeletonStatCard,
  SkeletonTable,
  SkeletonChart,
  SkeletonKPIStrip,
  DashboardSkeleton,
  PageTransition,
  FadeSlide,
};
