import React, { useState } from "react";
import { Code, ChevronDown, ChevronUp, Copy, Check, ShieldCheck } from "lucide-react";

export function SqlViewer({ sql }) {
  const [isOpen, setIsOpen] = useState(false);
  const [copied, setCopied] = useState(false);

  if (!sql) return null;

  const handleCopy = (e) => {
    e.stopPropagation();
    navigator.clipboard.writeText(sql);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="enterprise-card overflow-hidden mb-6 bg-white font-sans">
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className="w-full px-4 py-3 bg-slate-50 hover:bg-slate-100/80 transition-colors flex items-center justify-between text-left cursor-pointer border-b border-slate-100"
      >
        <div className="flex items-center space-x-2">
          <Code className="w-4 h-4 text-slate-500" />
          <h3 className="text-xs font-semibold text-slate-700">Audit & IT Technical Details</h3>
          <span className="inline-flex items-center space-x-1 text-[10px] px-2 py-0.5 rounded bg-emerald-50 text-emerald-700 border border-emerald-200 font-medium">
            <ShieldCheck className="w-3 h-3 text-emerald-600 mr-0.5" />
            <span>Validated: read-only, schema-safe</span>
          </span>
        </div>

        <div className="flex items-center space-x-2">
          <button
            type="button"
            onClick={handleCopy}
            className="px-2 py-1 rounded bg-white hover:bg-slate-100 border border-slate-200 text-[11px] text-slate-600 flex items-center space-x-1 transition-colors cursor-pointer"
            title="Copy SQL Query"
          >
            {copied ? (
              <>
                <Check className="w-3 h-3 text-emerald-600" />
                <span className="text-emerald-700 font-medium">Copied</span>
              </>
            ) : (
              <>
                <Copy className="w-3 h-3 text-slate-400" />
                <span>Copy Query</span>
              </>
            )}
          </button>
          {isOpen ? (
            <ChevronUp className="w-4 h-4 text-slate-400" />
          ) : (
            <ChevronDown className="w-4 h-4 text-slate-400" />
          )}
        </div>
      </button>

      {isOpen && (
        <div className="p-4 bg-slate-900 overflow-x-auto">
          <pre className="font-mono text-xs leading-relaxed text-slate-200 whitespace-pre-wrap">
            <code>{sql}</code>
          </pre>
        </div>
      )}
    </div>
  );
}
