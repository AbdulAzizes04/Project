import React from "react";
import { LucideIcon } from "lucide-react";

interface EmptyStateProps {
  icon: LucideIcon;
  title: string;
  description: string;
  primaryAction?: {
    label: string;
    onClick?: () => void;
    href?: string;
    icon?: LucideIcon;
  };
  secondaryAction?: {
    label: string;
    onClick?: () => void;
    href?: string;
    icon?: LucideIcon;
  };
  className?: string;
}

export function EmptyState({
  icon: Icon,
  title,
  description,
  primaryAction,
  secondaryAction,
  className = "",
}: EmptyStateProps) {
  return (
    <div
      className={`min-h-[280px] max-h-[320px] p-8 flex flex-col items-center justify-center text-center bg-white rounded-xl border border-dashed border-slate-300 shadow-sm ${className}`}
    >
      <div className="w-12 h-12 rounded-xl bg-slate-50 border border-slate-200/80 flex items-center justify-center text-slate-500 mb-3 shadow-inner">
        <Icon className="w-6 h-6 stroke-[1.75]" />
      </div>

      <h3 className="text-base font-bold text-slate-900 mb-1 tracking-tight">
        {title}
      </h3>

      <p className="text-xs sm:text-sm text-slate-500 max-w-md mb-5 leading-relaxed">
        {description}
      </p>

      {(primaryAction || secondaryAction) && (
        <div className="flex flex-wrap items-center justify-center gap-3">
          {primaryAction &&
            (primaryAction.href ? (
              <a
                href={primaryAction.href}
                className="btn-primary inline-flex items-center gap-2 text-xs font-semibold px-4 py-2"
              >
                {primaryAction.icon && (
                  <primaryAction.icon className="w-3.5 h-3.5" />
                )}
                {primaryAction.label}
              </a>
            ) : (
              <button
                type="button"
                onClick={primaryAction.onClick}
                className="btn-primary inline-flex items-center gap-2 text-xs font-semibold px-4 py-2"
              >
                {primaryAction.icon && (
                  <primaryAction.icon className="w-3.5 h-3.5" />
                )}
                {primaryAction.label}
              </button>
            ))}

          {secondaryAction &&
            (secondaryAction.href ? (
              <a
                href={secondaryAction.href}
                className="btn-secondary inline-flex items-center gap-2 text-xs font-semibold px-4 py-2"
              >
                {secondaryAction.icon && (
                  <secondaryAction.icon className="w-3.5 h-3.5" />
                )}
                {secondaryAction.label}
              </a>
            ) : (
              <button
                type="button"
                onClick={secondaryAction.onClick}
                className="btn-secondary inline-flex items-center gap-2 text-xs font-semibold px-4 py-2"
              >
                {secondaryAction.icon && (
                  <secondaryAction.icon className="w-3.5 h-3.5" />
                )}
                {secondaryAction.label}
              </button>
            ))}
        </div>
      )}
    </div>
  );
}
