import React from "react";
import { Building2, ShieldCheck, CheckCircle } from "lucide-react";

export function Header() {
  return (
    <header className="bg-white border-b border-slate-200 sticky top-0 z-50 shadow-xs">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        
        {/* Brand Logo & Name */}
        <div className="flex items-center space-x-3">
          <div className="w-9 h-9 rounded-lg bg-blue-800 flex items-center justify-center text-white shadow-xs">
            <Building2 className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h1 className="font-bold text-base tracking-tight text-slate-900 font-sans">
                Workday HR Analytics
              </h1>
              <span className="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-semibold bg-blue-50 text-blue-800 border border-blue-200/80">
                AI Reporting Assistant
              </span>
            </div>
            <p className="text-xs text-slate-500 font-sans">Natural-Language Enterprise Data Agent</p>
          </div>
        </div>

        {/* Status Badges */}
        <div className="hidden sm:flex items-center space-x-4 text-xs text-slate-600 font-sans">
          <div className="flex items-center space-x-1.5 bg-slate-50 px-3 py-1.5 rounded-md border border-slate-200">
            <ShieldCheck className="w-4 h-4 text-slate-600" />
            <span>Read-Only SQLite Compliance</span>
          </div>
          <div className="flex items-center space-x-1.5 bg-emerald-50 px-3 py-1.5 rounded-md border border-emerald-200 text-emerald-800 font-medium">
            <CheckCircle className="w-3.5 h-3.5 text-emerald-600" />
            <span>API Online</span>
          </div>
        </div>

      </div>
    </header>
  );
}
