import React from "react";
import { HelpCircle, ArrowRight } from "lucide-react";

export function ClarificationCard({
  question = "Which category or scope would you like to clarify?",
  options = ["Active Employees", "All Employees (Including Terminated)", "Employees Currently on Leave"],
  onSelectOption
}) {
  return (
    <div className="enterprise-card p-5 mb-6 bg-blue-50/50 border-blue-200 font-sans">
      <div className="flex items-start space-x-3">
        <div className="p-2 rounded-md bg-blue-100 text-blue-800 shrink-0">
          <HelpCircle className="w-5 h-5" />
        </div>

        <div className="flex-1 min-w-0">
          <div className="flex items-center space-x-2 mb-1">
            <span className="text-xs font-semibold uppercase tracking-wider text-blue-900">
              Analyst Clarification
            </span>
          </div>

          <p className="text-xs font-medium text-slate-800 leading-relaxed mb-3">
            {question}
          </p>

          <div className="flex flex-wrap gap-2">
            {options.map((opt, idx) => (
              <button
                key={idx}
                type="button"
                onClick={() => onSelectOption && onSelectOption(opt)}
                className="px-3 py-1.5 rounded-md bg-white hover:bg-blue-100/60 border border-slate-200 text-xs font-medium text-slate-800 hover:text-blue-900 transition-colors flex items-center space-x-1.5 cursor-pointer shadow-xs"
              >
                <span>{opt}</span>
                <ArrowRight className="w-3 h-3 text-slate-400" />
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
