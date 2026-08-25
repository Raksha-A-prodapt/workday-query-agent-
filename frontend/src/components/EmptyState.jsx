import React from "react";
import { Building2, ShieldCheck, CheckCircle2 } from "lucide-react";

export function EmptyState() {
  return (
    <div className="enterprise-card p-8 text-center max-w-3xl mx-auto my-8 bg-white font-sans">
      <div className="w-14 h-14 rounded-xl bg-blue-50 border border-blue-200 flex items-center justify-center mx-auto mb-4 text-blue-800">
        <Building2 className="w-7 h-7" />
      </div>

      <h3 className="text-lg font-bold text-slate-900 mb-1">
        Workday HR Executive Reporting Assistant
      </h3>
      <p className="text-xs text-slate-600 max-w-md mx-auto mb-6">
        Ask natural-language questions above to query employee headcount, department budgets, leave balances, and open job requisitions.
      </p>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-left">
        <div className="p-3.5 rounded-lg bg-slate-50 border border-slate-200">
          <CheckCircle2 className="w-4 h-4 text-emerald-600 mb-1.5" />
          <h4 className="text-xs font-semibold text-slate-800">HR Data Scope</h4>
          <p className="text-[11px] text-slate-500 mt-0.5">Headcount, departments, regions, salaries, time off, and job openings.</p>
        </div>

        <div className="p-3.5 rounded-lg bg-slate-50 border border-slate-200">
          <ShieldCheck className="w-4 h-4 text-blue-700 mb-1.5" />
          <h4 className="text-xs font-semibold text-slate-800">Audit Compliance</h4>
          <p className="text-[11px] text-slate-500 mt-0.5">Read-only SQL AST validation & SQLite EXPLAIN verification.</p>
        </div>

        <div className="p-3.5 rounded-lg bg-slate-50 border border-slate-200">
          <CheckCircle2 className="w-4 h-4 text-blue-700 mb-1.5" />
          <h4 className="text-xs font-semibold text-slate-800">Verified Insights</h4>
          <p className="text-[11px] text-slate-500 mt-0.5">Zero ungrounded claims; answer text strictly cross-checked with raw records.</p>
        </div>
      </div>
    </div>
  );
}
