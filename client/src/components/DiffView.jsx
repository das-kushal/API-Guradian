import React from "react";
import { GitCompare, Trash2, Edit3, Plus, Shield, AlertTriangle, FileWarning } from "lucide-react";
import { Card, CardHeader } from "./ui/Card";
import { Badge } from "./ui/Badge";

function DiffView({ diff }) {
  if (!diff) return null;

  const hasChanges =
    (diff.removed_endpoints?.length > 0) ||
    (diff.added_endpoints?.length > 0) ||
    (diff.method_changes?.length > 0) ||
    (diff.parameter_changes?.length > 0) ||
    (diff.pii_fields_detected?.length > 0) ||
    (diff.naming_issues?.length > 0) ||
    (diff.missing_descriptions?.length > 0) ||
    (diff.schema_changes?.removed_schemas?.length > 0) ||
    (diff.schema_changes?.field_changes?.length > 0);

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
        title="API Diff Analysis"
        description="Deterministic analysis of structural changes."
        icon={GitCompare}
      />

      <div className="space-y-6">
        {/* Removed Endpoints */}
        <DiffSection
          items={diff.removed_endpoints}
          title="Removed Endpoints"
          icon={Trash2}
          colorClass="red"
          renderItem={(ep) => <span className="font-mono text-sm text-slate-300">{ep}</span>}
        />

        {/* Added Endpoints */}
        <DiffSection
          items={diff.added_endpoints}
          title="Added Endpoints"
          icon={Plus}
          colorClass="emerald"
          renderItem={(ep) => <span className="font-mono text-sm text-slate-300">{ep}</span>}
        />

        {/* Method Changes */}
        {diff.method_changes?.length > 0 && (
          <div>
            <SectionHeader title="Method Changes" icon={Edit3} colorClass="amber" />
            <div className="space-y-2">
              {diff.method_changes.map((mc, idx) => (
                <div key={idx} className="bg-slate-950/50 rounded-lg border border-amber-500/20 p-3">
                  <div className="font-mono text-xs text-slate-500 mb-2">{mc.path}</div>
                  <div className="flex flex-wrap gap-2">
                    {mc.removed_methods?.map((m, i) => (
                      <Badge key={`r-${i}`} variant="danger" className="font-mono text-xs">
                        - {m.toUpperCase()}
                      </Badge>
                    ))}
                    {mc.added_methods?.map((m, i) => (
                      <Badge key={`a-${i}`} variant="success" className="font-mono text-xs">
                        + {m.toUpperCase()}
                      </Badge>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* PII Fields Detected */}
        <DiffSection
          items={diff.pii_fields_detected}
          title="PII Fields Detected"
          icon={Shield}
          colorClass="purple"
          renderItem={(f) => <span className="font-mono text-sm text-purple-300">{f}</span>}
        />

        {/* Naming Issues */}
        <DiffSection
          items={diff.naming_issues}
          title="Naming Anti-Patterns"
          icon={AlertTriangle}
          colorClass="amber"
          renderItem={(issue) => <span className="text-sm text-slate-300">{issue}</span>}
        />

        {/* Missing Descriptions */}
        <DiffSection
          items={diff.missing_descriptions}
          title="Missing Descriptions"
          icon={FileWarning}
          colorClass="slate"
          renderItem={(ep) => <span className="font-mono text-sm text-slate-400">{ep}</span>}
        />
      </div>
    </Card>
  );
}

/** Reusable section header */
function SectionHeader({ title, icon: Icon, colorClass }) {
  return (
    <h4 className={`flex items-center gap-2 text-sm font-medium text-${colorClass}-400 mb-3 uppercase tracking-wider`}>
      <Icon size={14} /> {title}
    </h4>
  );
}

/** Reusable diff section for simple list items */
function DiffSection({ items, title, icon, colorClass, renderItem }) {
  if (!items || items.length === 0) return null;
  return (
    <div>
      <SectionHeader title={title} icon={icon} colorClass={colorClass} />
      <div className={`bg-slate-950/50 rounded-lg border border-${colorClass}-500/20 overflow-hidden`}>
        {items.map((item, idx) => (
          <div key={idx} className={`px-4 py-3 border-b border-${colorClass}-500/10 last:border-0 flex items-center gap-3`}>
            {renderItem(item)}
          </div>
        ))}
      </div>
    </div>
  );
}

export default DiffView;
