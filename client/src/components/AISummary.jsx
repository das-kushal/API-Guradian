import React from "react";
import { Sparkles, AlertTriangle, Shield, Info, Loader2 } from "lucide-react";
import { Card, CardHeader } from "./ui/Card";

function AISummary({ ai, isStreaming, rawText }) {
  // Helper to parse potential Python-stringified lists/objects
  const parseValue = (value) => {
    if (typeof value !== 'string') return value;

    const trimmed = value.trim();
    if ((trimmed.startsWith('[') && trimmed.endsWith(']')) || 
        (trimmed.startsWith('{') && trimmed.endsWith('}'))) {
      try {
        const jsonString = trimmed.replace(/'/g, '"')
                                  .replace(/None/g, 'null')
                                  .replace(/True/g, 'true')
                                  .replace(/False/g, 'false');
        return JSON.parse(jsonString);
      } catch (e) {
        return value;
      }
    }
    return value;
  };

  const renderValue = (value) => {
    const parsed = parseValue(value);

    if (Array.isArray(parsed)) {
      if (parsed.length === 0) return <span className="text-slate-500 italic">None</span>;
      return (
        <ul className="list-disc list-inside space-y-1 ml-1">
          {parsed.map((item, i) => (
            <li key={i} className="text-slate-300 text-sm">
              {typeof item === 'object' ? renderValue(item) : String(item)}
            </li>
          ))}
        </ul>
      );
    }

    if (typeof parsed === 'object' && parsed !== null) {
      return (
        <div className="bg-slate-900/50 rounded p-3 text-sm space-y-2 border border-slate-700/50">
          {Object.entries(parsed).map(([k, v], i) => (
            <div key={i} className="grid grid-cols-[auto_1fr] gap-2">
              <span className="font-mono text-blue-400/80">{k}:</span>
              <span className="text-slate-300 break-words">{typeof v === 'object' ? JSON.stringify(v) : String(v)}</span>
            </div>
          ))}
        </div>
      );
    }

    return <span className="text-slate-300 text-sm leading-relaxed">{String(parsed)}</span>;
  };

  const renderContent = () => {
    // Streaming state — show raw text with a cursor
    if (isStreaming) {
      return (
        <div className="space-y-3">
          <div className="flex items-center gap-2 text-blue-400 text-sm mb-4">
            <Loader2 size={14} className="animate-spin" />
            <span>AI is analyzing your API changes...</span>
          </div>
          <div className="font-mono text-xs text-slate-400 bg-slate-950/50 rounded-lg p-4 border border-blue-500/10 min-h-[120px] whitespace-pre-wrap break-words leading-relaxed">
            {rawText}
            <span className="inline-block w-2 h-4 bg-blue-400 ml-0.5 animate-pulse align-middle" />
          </div>
        </div>
      );
    }

    if (!ai) {
      return (
        <div className="flex items-center gap-2 text-slate-500 text-sm">
          <Loader2 size={14} className="animate-spin" />
          Waiting for analysis...
        </div>
      );
    }

    if (ai.error) {
      return (
        <div className="text-red-400 text-sm bg-red-500/10 rounded-lg p-3 border border-red-500/20">
          ⚠️ {ai.error}
        </div>
      );
    }

    if (typeof ai === 'string') {
      return <p className="text-slate-300 text-sm leading-relaxed">{ai}</p>;
    }
    
    if (typeof ai === 'object') {
      return (
        <div className="space-y-6">
          {Object.entries(ai).map(([key, value], idx) => {
            const formattedKey = key.replace(/_/g, ' ');
            let icon = <Info size={16} className="text-blue-400" />;
            
            if (key.toLowerCase().includes('risk') || key.toLowerCase().includes('break')) {
              icon = <AlertTriangle size={16} className="text-amber-400" />;
            } else if (key.toLowerCase().includes('security') || key.toLowerCase().includes('pii')) {
              icon = <Shield size={16} className="text-emerald-400" />;
            }

            return (
              <div key={idx} className="group">
                <h4 className="flex items-center gap-2 text-sm font-semibold text-slate-100 mb-2 capitalize">
                  {icon}
                  {formattedKey}
                </h4>
                <div className="pl-6 border-l-2 border-slate-800 group-hover:border-blue-500/30 transition-colors">
                  {renderValue(value)}
                </div>
              </div>
            );
          })}
        </div>
      );
    }
  };

  return (
    <Card className="h-full bg-gradient-to-br from-slate-950 to-slate-900 border-white/5">
      <div className="absolute top-0 right-0 p-4 opacity-[0.03]">
        <Sparkles size={120} />
      </div>
      
      <CardHeader 
        title="AI Security Analysis" 
        description={isStreaming ? "Generating insights..." : "Automated insights on potential vulnerabilities."}
        icon={isStreaming ? Loader2 : Sparkles}
        className="pb-2 border-b border-white/5 mb-4"
      />

      <div className="relative z-10">
        {renderContent()}
      </div>
    </Card>
  );
}

export default AISummary;
