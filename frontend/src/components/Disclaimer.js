import React from 'react';
import { AlertTriangle } from 'lucide-react';

/**
 * Legal Disclaimer Component
 * Displays a legal disclaimer for financial calculations throughout the app.
 */
export default function Disclaimer({ variant = 'default', className = '' }) {
  const disclaimerText = "ExportFlow calculations are based on user-provided and/or government-synced data. ExportFlow does not assume legal liability for incorrect declarations, filings, or compliance outcomes.";

  if (variant === 'compact') {
    return (
      <div className={`text-xs text-muted-foreground/70 flex items-start gap-2 ${className}`}>
        <AlertTriangle className="w-3 h-3 flex-shrink-0 mt-0.5" />
        <p>{disclaimerText}</p>
      </div>
    );
  }

  if (variant === 'footer') {
    return (
      <div className={`mt-8 pt-6 border-t border-border ${className}`}>
        <div className="flex items-start gap-3 p-4 rounded-lg bg-amber-500/5 border border-amber-500/20">
          <AlertTriangle className="w-5 h-5 text-amber flex-shrink-0 mt-0.5" />
          <div>
            <p className="text-sm font-medium text-amber mb-1">Important Disclaimer</p>
            <p className="text-xs text-muted-foreground leading-relaxed">
              {disclaimerText} Users are advised to verify all calculations with qualified professionals 
              before making any business or compliance decisions.
            </p>
          </div>
        </div>
      </div>
    );
  }

  // Default variant
  return (
    <div className={`p-4 rounded-lg bg-zinc-800/50 border border-zinc-700/50 ${className}`}>
      <div className="flex items-start gap-3">
        <AlertTriangle className="w-5 h-5 text-amber-400 flex-shrink-0 mt-0.5" />
        <p className="text-xs text-zinc-400 leading-relaxed">
          <strong className="text-zinc-300">Disclaimer:</strong> {disclaimerText}
        </p>
      </div>
    </div>
  );
}

// Export a shorter disclaimer text for inline use
export const DISCLAIMER_TEXT = "ExportFlow calculations are based on user-provided and/or government-synced data. ExportFlow does not assume legal liability for incorrect declarations, filings, or compliance outcomes.";
