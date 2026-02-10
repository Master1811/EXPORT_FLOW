import React from 'react';

/**
 * Skeleton Loader Components for slow network conditions
 * Used during lazy loading and API calls
 */

export const SkeletonCard = ({ className = '' }) => (
  <div className={`animate-pulse bg-card border border-border rounded-lg p-6 ${className}`}>
    <div className="h-4 bg-muted rounded w-3/4 mb-4"></div>
    <div className="h-3 bg-muted rounded w-1/2 mb-2"></div>
    <div className="h-3 bg-muted rounded w-2/3"></div>
  </div>
);

export const SkeletonTable = ({ rows = 5, cols = 4 }) => (
  <div className="animate-pulse">
    {/* Header */}
    <div className="flex gap-4 p-4 border-b border-border">
      {Array(cols).fill(0).map((_, i) => (
        <div key={i} className="h-4 bg-muted rounded flex-1"></div>
      ))}
    </div>
    {/* Rows */}
    {Array(rows).fill(0).map((_, rowIndex) => (
      <div key={rowIndex} className="flex gap-4 p-4 border-b border-border">
        {Array(cols).fill(0).map((_, colIndex) => (
          <div key={colIndex} className="h-4 bg-muted rounded flex-1"></div>
        ))}
      </div>
    ))}
  </div>
);

export const SkeletonDashboard = () => (
  <div className="space-y-6 animate-fade-in">
    {/* Header */}
    <div className="animate-pulse">
      <div className="h-8 bg-muted rounded w-48 mb-2"></div>
      <div className="h-4 bg-muted rounded w-64"></div>
    </div>
    
    {/* Stat Cards */}
    <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
      {Array(4).fill(0).map((_, i) => (
        <SkeletonCard key={i} />
      ))}
    </div>
    
    {/* Charts */}
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <div className="animate-pulse bg-card border border-border rounded-lg p-6 h-64">
        <div className="h-4 bg-muted rounded w-1/3 mb-4"></div>
        <div className="h-40 bg-muted rounded"></div>
      </div>
      <div className="animate-pulse bg-card border border-border rounded-lg p-6 h-64">
        <div className="h-4 bg-muted rounded w-1/3 mb-4"></div>
        <div className="h-40 bg-muted rounded"></div>
      </div>
    </div>
    
    {/* Table */}
    <div className="bg-card border border-border rounded-lg overflow-hidden">
      <SkeletonTable rows={5} cols={6} />
    </div>
  </div>
);

export const SkeletonForm = ({ fields = 4 }) => (
  <div className="animate-pulse space-y-4">
    {Array(fields).fill(0).map((_, i) => (
      <div key={i} className="space-y-2">
        <div className="h-4 bg-muted rounded w-24"></div>
        <div className="h-10 bg-muted rounded"></div>
      </div>
    ))}
    <div className="h-10 bg-primary/30 rounded w-32 mt-6"></div>
  </div>
);

export const SkeletonList = ({ items = 5 }) => (
  <div className="animate-pulse space-y-3">
    {Array(items).fill(0).map((_, i) => (
      <div key={i} className="flex items-center gap-4 p-4 bg-card border border-border rounded-lg">
        <div className="w-10 h-10 bg-muted rounded-full"></div>
        <div className="flex-1 space-y-2">
          <div className="h-4 bg-muted rounded w-3/4"></div>
          <div className="h-3 bg-muted rounded w-1/2"></div>
        </div>
        <div className="h-6 bg-muted rounded w-16"></div>
      </div>
    ))}
  </div>
);

export default {
  SkeletonCard,
  SkeletonTable,
  SkeletonDashboard,
  SkeletonForm,
  SkeletonList,
};
