import React from "react";
import { GitCompare, Trash2, Edit3 } from "lucide-react";
import { Card, CardHeader } from "./ui/Card";
import { Badge } from "./ui/Badge";

function DiffView({ diff }) {
  const hasChanges = 
    (diff?.removed_endpoints && diff.removed_endpoints.length > 0) ||
    (diff?.method_changes && Object.keys(diff.method_changes).length > 0);

  if (!hasChanges) {
    return (
      <Card className="h-full flex flex-col items-center justify-center py-12 text-center">
        <div className="w-12 h-12 bg-slate-800 rounded-full flex items-center justify-center mb-4">
          <GitCompare className="text-slate-500" />
        </div>
        <h3 className="text-lg font-medium text-slate-300">No Breaking Changes Detected</h3>
        <p className="text-slate-500 text-sm mt-1">The interface appears compatible.</p>
      </Card>
    );
  }

  return (
    <Card className="h-full">
      <CardHeader 
        title="Breaking Changes" 
        description="Detected modifications that may impact API consumers."
        icon={GitCompare}
      />
      
      <div className="space-y-6">
        {/* Removed Endpoints */}
        {diff.removed_endpoints?.length > 0 && (
          <div>
            <h4 className="flex items-center gap-2 text-sm font-medium text-red-400 mb-3 uppercase tracking-wider">
              <Trash2 size={14} /> Removed Endpoints
            </h4>
            <div className="bg-slate-950/50 rounded-lg border border-red-500/20 overflow-hidden">
              {diff.removed_endpoints.map((endpoint, idx) => (
                <div 
                  key={idx} 
                  className="px-4 py-3 border-b border-red-500/10 last:border-0 flex items-center gap-3"
                >
                  <span className="font-mono text-sm text-slate-300">{endpoint}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Method Changes */}
        {diff.method_changes && Object.keys(diff.method_changes).length > 0 && (
          <div>
            <h4 className="flex items-center gap-2 text-sm font-medium text-amber-400 mb-3 uppercase tracking-wider">
              <Edit3 size={14} /> Method Changes
            </h4>
            <div className="space-y-3">
              {Object.entries(diff.method_changes).map(([endpoint, changes], idx) => (
                <div key={idx} className="bg-slate-950/50 rounded-lg border border-amber-500/20 p-4">
                  <div className="mb-2 font-mono text-xs text-slate-500 break-all">{endpoint}</div>
                  <div className="flex flex-wrap gap-2">
                    {Object.entries(changes).map(([key, value], i) => (
                      <Badge key={i} variant="warning" className="font-mono">
                        {key}: {JSON.stringify(value)}
                      </Badge>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </Card>
  );
}

export default DiffView;
