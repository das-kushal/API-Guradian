import React from "react";
import { AlertTriangle, CheckCircle, AlertOctagon } from "lucide-react";
import { motion } from "framer-motion";
import { Card } from "./ui/Card";

function RiskPanel({ score }) {
  const getRiskLevel = (s) => {
    if (s <= 3) return { label: "Low Risk", color: "text-emerald-400", bg: "bg-emerald-500/10", border: "border-emerald-500/20", icon: CheckCircle };
    if (s <= 7) return { label: "Medium Risk", color: "text-amber-400", bg: "bg-amber-500/10", border: "border-amber-500/20", icon: AlertTriangle };
    return { label: "High Risk", color: "text-red-400", bg: "bg-red-500/10", border: "border-red-500/20", icon: AlertOctagon };
  };

  const { label, color, bg, border, icon: Icon } = getRiskLevel(score);
  
  // Calculate circle circumference for SVG animation
  const radius = 36;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (score / 10) * circumference;

  return (
    <Card className="flex items-center justify-between relative overflow-hidden">
      {/* Background Glow */}
      <div className={`absolute -right-10 -top-10 w-40 h-40 rounded-full blur-[60px] opacity-20 ${bg.replace("/10", "")}`} />

      <div className="z-10">
        <div className="flex items-center gap-3 mb-1">
          <div className={`p-2 rounded-lg ${bg} ${border} ring-1 ring-inset ring-white/5`}>
            <Icon className={`w-5 h-5 ${color}`} />
          </div>
          <h2 className="text-xl font-semibold text-slate-100">Security Risk Assessment</h2>
        </div>
        <p className="text-slate-400 text-sm max-w-md">
          Based on the analysis of breaking changes and potential security vulnerabilities introduced in this update.
        </p>
      </div>

      <div className="flex items-center gap-6 z-10">
        <div className="text-right">
          <div className={`text-2xl font-bold ${color}`}>{label}</div>
          <div className="text-xs text-slate-500 font-mono uppercase tracking-wider">Risk Level</div>
        </div>

        {/* Circular Score Indicator */}
        <div className="relative w-24 h-24 flex items-center justify-center">
          <svg className="w-full h-full -rotate-90 transform">
            <circle
              cx="48"
              cy="48"
              r={radius}
              stroke="currentColor"
              strokeWidth="8"
              fill="transparent"
              className="text-slate-800"
            />
            <motion.circle
              initial={{ strokeDashoffset: circumference }}
              animate={{ strokeDashoffset }}
              transition={{ duration: 1.5, ease: "easeOut" }}
              cx="48"
              cy="48"
              r={radius}
              stroke="currentColor"
              strokeWidth="8"
              fill="transparent"
              strokeDasharray={circumference}
              strokeLinecap="round"
              className={color}
            />
          </svg>
          <div className="absolute inset-0 flex items-center justify-center flex-col">
            <span className={`text-2xl font-bold ${color}`}>{score}</span>
            <span className="text-[10px] text-slate-500 uppercase">/10</span>
          </div>
        </div>
      </div>
    </Card>
  );
}

export default RiskPanel;
