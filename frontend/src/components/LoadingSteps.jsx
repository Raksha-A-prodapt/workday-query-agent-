import React from "react";
import { Check, Loader2 } from "lucide-react";

export const PLAIN_STEPS = [
  "Understanding your question",
  "Looking up the right HR data",
  "Preparing your answer",
  "Double-checking the numbers",
];

export function LoadingSteps({ currentStepIndex = 0 }) {
  const mappedStepIndex = Math.min(Math.floor((currentStepIndex / 5) * 3), 3);
  const progressPercent = Math.round(((mappedStepIndex + 1) / PLAIN_STEPS.length) * 100);

  return (
    <div className="enterprise-card p-5 mb-6 bg-white font-sans">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center space-x-2">
          <Loader2 className="w-4 h-4 text-blue-700 animate-spin" />
          <span className="text-sm font-semibold text-slate-800">
            System is retrieving HR insights...
          </span>
        </div>
        <span className="text-xs font-medium text-slate-500">{progressPercent}%</span>
      </div>

      {/* Clean Horizontal Progress Bar */}
      <div className="w-full bg-slate-100 rounded-full h-2 mb-4 overflow-hidden">
        <div
          className="bg-blue-700 h-2 rounded-full transition-all duration-300 ease-out"
          style={{ width: `${progressPercent}%` }}
        ></div>
      </div>

      {/* Plain Language Step Indicators */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
        {PLAIN_STEPS.map((stepLabel, idx) => {
          const isDone = idx < mappedStepIndex;
          const isCurrent = idx === mappedStepIndex;

          return (
            <div
              key={idx}
              className={`p-2.5 rounded-lg border text-xs flex items-center space-x-2 transition-colors ${
                isCurrent
                  ? "bg-blue-50 border-blue-200 text-blue-900 font-medium"
                  : isDone
                  ? "bg-slate-50 border-slate-200 text-slate-700"
                  : "bg-slate-50/50 border-slate-100 text-slate-400"
              }`}
            >
              <div
                className={`w-4 h-4 rounded-full flex items-center justify-center text-[10px] shrink-0 ${
                  isDone
                    ? "bg-emerald-600 text-white"
                    : isCurrent
                    ? "bg-blue-700 text-white font-bold"
                    : "bg-slate-200 text-slate-500"
                }`}
              >
                {isDone ? <Check className="w-2.5 h-2.5 stroke-[3]" /> : idx + 1}
              </div>
              <span className="truncate">{stepLabel}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
