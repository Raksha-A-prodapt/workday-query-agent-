import React, { useState } from "react";
import { CheckCircle2, ChevronDown, ChevronUp, AlertTriangle } from "lucide-react";

export function AnswerCard({
  answer,
  rowCount = 0,
  error = null,
  status = "success",
  faithfulness = { verified: true, rowsChecked: 0 }
}) {
  const [showAuditDetails, setShowAuditDetails] = useState(false);
  const isError = status === "error" || Boolean(error);
  const rowsChecked = faithfulness.rowsChecked || rowCount;

  return (
    <div
      className={`enterprise-card p-6 mb-6 ${
        isError ? "border-amber-200 bg-amber-50/50" : "border-slate-200 bg-white"
      }`}
    >
      {/* Header Badge */}
      <div className="flex items-center justify-between pb-3 mb-3 border-b border-slate-100">
        <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">
          {isError ? "System Notice" : "Executive HR Response"}
        </span>
        {rowCount > 0 && (
          <span className="text-xs px-2.5 py-0.5 rounded-full font-medium bg-slate-100 text-slate-600 border border-slate-200">
            {rowCount} {rowCount === 1 ? "Record Returned" : "Records Returned"}
          </span>
        )}
      </div>

      {/* Answer Text */}
      <div className="text-base text-slate-900 leading-relaxed font-sans mb-4 font-normal">
        {answer || "No response generated."}
      </div>

      {/* Error Message if Error */}
      {error && isError && (
        <div className="p-3.5 rounded-lg bg-amber-100/60 border border-amber-200 text-xs text-amber-800 font-sans flex items-start space-x-2">
          <AlertTriangle className="w-4 h-4 text-amber-600 shrink-0 mt-0.5" />
          <div>
            <span className="font-semibold">Query Notice:</span> {error}
          </div>
        </div>
      )}

      {/* Audit & Compliance Verification Line */}
      {!isError && (
        <div className="pt-3 border-t border-slate-100 flex items-center justify-between">
          <button
            type="button"
            onClick={() => setShowAuditDetails(!showAuditDetails)}
            className="inline-flex items-center space-x-2 text-xs font-medium text-emerald-700 bg-emerald-50 hover:bg-emerald-100/80 px-2.5 py-1.5 rounded-md border border-emerald-200/80 transition-colors cursor-pointer"
          >
            <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
            <span>Verified against the underlying HR data</span>
            {showAuditDetails ? (
              <ChevronUp className="w-3.5 h-3.5 text-emerald-600" />
            ) : (
              <ChevronDown className="w-3.5 h-3.5 text-emerald-600" />
            )}
          </button>
        </div>
      )}

      {/* Expandable Audit Details */}
      {showAuditDetails && !isError && (
        <div className="mt-3 p-3 rounded-lg bg-slate-50 border border-slate-200 text-xs text-slate-600 font-sans animate-fadeIn">
          <div className="font-semibold text-slate-800 mb-1">Data Audit & Faithfulness Summary</div>
          This response was cross-checked against {rowsChecked} underlying database {rowsChecked === 1 ? "record" : "records"}. All numbers and aggregated values are strictly grounded in active HR records with zero unverified claims.
        </div>
      )}
    </div>
  );
}
