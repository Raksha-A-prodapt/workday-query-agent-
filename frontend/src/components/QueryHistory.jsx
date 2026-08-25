import React, { useState } from "react";
import { History, Trash2, CornerDownRight, Clock } from "lucide-react";

export function QueryHistory({ history, onSelectQuestion, onClearHistory }) {
  const [isOpen, setIsOpen] = useState(false);

  if (!history || history.length === 0) return null;

  return (
    <div className="mb-6 font-sans">
      <div className="flex items-center justify-between mb-2">
        <button
          type="button"
          onClick={() => setIsOpen(!isOpen)}
          className="flex items-center space-x-1.5 text-xs font-semibold text-slate-500 hover:text-blue-800 transition-colors uppercase tracking-wider cursor-pointer"
        >
          <History className="w-3.5 h-3.5 text-blue-700" />
          <span>Recent Query Thread ({history.length})</span>
        </button>

        {isOpen && (
          <button
            type="button"
            onClick={onClearHistory}
            className="flex items-center space-x-1 text-xs text-slate-400 hover:text-red-600 transition-colors cursor-pointer"
          >
            <Trash2 className="w-3 h-3" />
            <span>Clear History</span>
          </button>
        )}
      </div>

      {isOpen && (
        <div className="enterprise-card p-3 bg-white space-y-1.5">
          {history.map((q, idx) => {
            const isFollowUp = idx > 0 && (q.toLowerCase().includes("break") || q.toLowerCase().includes("show") || q.toLowerCase().includes("what about"));

            return (
              <div
                key={idx}
                className={`flex items-center ${isFollowUp ? "ml-5 pl-2 border-l-2 border-blue-200" : ""}`}
              >
                <button
                  type="button"
                  onClick={() => onSelectQuestion(q)}
                  className="w-full text-left px-3 py-2 rounded-md hover:bg-slate-50 transition-colors text-xs text-slate-800 flex items-center justify-between group cursor-pointer"
                >
                  <div className="flex items-center space-x-2 truncate">
                    {isFollowUp ? (
                      <CornerDownRight className="w-3.5 h-3.5 text-blue-600 shrink-0" />
                    ) : (
                      <Clock className="w-3.5 h-3.5 text-slate-400 shrink-0" />
                    )}
                    <span className="truncate">{q}</span>
                    {isFollowUp && (
                      <span className="text-[10px] px-1.5 py-0.5 rounded bg-blue-50 text-blue-700 font-medium">
                        Refinement
                      </span>
                    )}
                  </div>
                </button>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
