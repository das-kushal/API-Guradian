import React from "react";
import { motion } from "framer-motion";
import { clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs) {
  return twMerge(clsx(inputs));
}

const variants = {
  primary: "bg-gradient-to-r from-blue-500 to-indigo-600 text-white shadow-lg shadow-blue-500/25 border-transparent hover:brightness-110",
  secondary: "bg-slate-800 text-slate-100 border-slate-700 hover:bg-slate-700",
  outline: "bg-transparent border-slate-600 text-slate-300 hover:border-slate-400 hover:text-white",
  ghost: "bg-transparent border-transparent text-slate-400 hover:text-white hover:bg-white/5",
  danger: "bg-red-500/10 text-red-400 border-red-500/20 hover:bg-red-500/20"
};

const sizes = {
  sm: "px-3 py-1.5 text-xs",
  md: "px-4 py-2 text-sm",
  lg: "px-6 py-3 text-base"
};

export const Button = ({ 
  children, 
  variant = "primary", 
  size = "md", 
  className, 
  isLoading,
  ...props 
}) => {
  return (
    <motion.button
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      className={cn(
        "inline-flex items-center justify-center rounded-lg font-medium transition-all duration-200 border disabled:opacity-50 disabled:cursor-not-allowed",
        variants[variant],
        sizes[size],
        className
      )}
      disabled={isLoading}
      {...props}
    >
      {isLoading ? (
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin" />
          <span>Loading...</span>
        </div>
      ) : children}
    </motion.button>
  );
};
