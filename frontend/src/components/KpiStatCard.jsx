import React from "react";
import { Users, DollarSign, Calendar, Briefcase, TrendingUp } from "lucide-react";
import { formatColumnHeader, formatCellValue } from "../utils/formatData";

export function KpiStatCard({ label, value }) {
  const lowerLabel = (label || "").toLowerCase();

  let Icon = TrendingUp;
  if (lowerLabel.includes("headcount") || lowerLabel.includes("employee")) Icon = Users;
  else if (lowerLabel.includes("leave")) Icon = Calendar;
  else if (lowerLabel.includes("job") || lowerLabel.includes("opening")) Icon = Briefcase;
  else if (lowerLabel.includes("salary") || lowerLabel.includes("budget")) Icon = DollarSign;

  const formattedVal = formatCellValue(value, label);
  const formattedTitle = formatColumnHeader(label);

  return (
    <div className="enterprise-card p-6 mb-6 bg-white flex items-center justify-between font-sans">
      <div>
        <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">
          Executive Metric Summary
        </span>
        <h3 className="text-xs font-medium text-slate-600 mt-1">{formattedTitle}</h3>
        {/* Clear Large Number in Clean Sans Serif Inter */}
        <div className="text-4xl font-bold text-slate-900 tracking-tight mt-2 font-sans">
          {formattedVal}
        </div>
      </div>

      <div className="w-12 h-12 rounded-lg bg-blue-50 border border-blue-200 flex items-center justify-center text-blue-800 shrink-0">
        <Icon className="w-6 h-6" />
      </div>
    </div>
  );
}
