import React from "react";
import { cn } from "./Button"; // Reusing cn utility

export const Card = ({ children, className, ...props }) => {
  return (
    <div 
      className={cn(
        "glass-panel rounded-xl p-6 relative overflow-hidden",
        className
      )} 
      {...props}
    >
      {children}
    </div>
  );
};

export const CardHeader = ({ title, description, icon: Icon, className }) => {
  return (
    <div className={cn("mb-4", className)}>
      <div className="flex items-center gap-3 mb-2">
        {Icon && (
          <div className="p-2 rounded-lg bg-white/5 text-blue-400 ring-1 ring-white/10">
            <Icon size={20} />
          </div>
        )}
        <h3 className="text-lg font-semibold text-slate-100 leading-none">
          {title}
        </h3>
      </div>
      {description && (
        <p className="text-sm text-slate-400 leading-relaxed ml-11">
          {description}
        </p>
      )}
    </div>
  );
};
