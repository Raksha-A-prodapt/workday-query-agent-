import React from "react";
import { Search, Sparkles, X } from "lucide-react";

export function QueryInput({ value, onChange, onSubmit, loading }) {
  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      onSubmit();
    }
  };

  return (
    <div className="enterprise-card p-2 mb-6 bg-white shadow-sm">
      <div className="flex items-center px-3 py-1 space-x-3">
        <Search className="w-5 h-5 text-slate-400 shrink-0" />
        
        <input
          type="text"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask an HR question (e.g. How many employees are currently on leave?)"
          disabled={loading}
          className="w-full bg-transparent text-slate-900 placeholder-slate-400 text-sm font-sans focus:outline-none disabled:opacity-50 py-2"
        />

        {value && !loading && (
          <button
            type="button"
            onClick={() => onChange("")}
            className="p-1 rounded-md text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition-colors"
            title="Clear text"
          >
            <X className="w-4 h-4" />
          </button>
        )}

        <button
          type="button"
          onClick={() => onSubmit()}
          disabled={loading || !value.trim()}
          className="px-5 py-2.5 rounded-lg bg-blue-800 hover:bg-blue-900 text-white font-medium text-xs flex items-center space-x-2 shadow-xs disabled:opacity-50 disabled:cursor-not-allowed transition-colors shrink-0 cursor-pointer"
        >
          <Sparkles className="w-3.5 h-3.5" />
          <span>{loading ? "Searching..." : "Ask AI"}</span>
        </button>
      </div>
    </div>
  );
}
