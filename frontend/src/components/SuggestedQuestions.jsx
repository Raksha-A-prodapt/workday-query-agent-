import React, { useState } from "react";
import { HelpCircle, Users, Building2, Calendar, DollarSign, Briefcase, Clock, RefreshCw, MapPin, Award } from "lucide-react";

const QUESTION_POOL = [
  { icon: Users, label: "How many active employees are there?", desc: "Active headcount summary" },
  { icon: Building2, label: "Show employee count by department.", desc: "Department headcount breakdown" },
  { icon: Calendar, label: "How many employees are currently on leave?", desc: "On-leave status query" },
  { icon: DollarSign, label: "What is the average salary by department?", desc: "Department compensation analytics" },
  { icon: Briefcase, label: "How many open job positions are there?", desc: "Recruiting open requisitions" },
  { icon: Clock, label: "What is the average time to fill a role?", desc: "Time-to-fill metric by department" },
  { icon: MapPin, label: "Show approved leave requests by region.", desc: "Regional time off distribution" },
  { icon: Award, label: "Show department name and department head.", desc: "Department executive directors" },
];

export function SuggestedQuestions({ onSelectQuestion }) {
  const [startIndex, setStartIndex] = useState(0);

  const handleShuffle = () => {
    setStartIndex((prev) => (prev + 3) % QUESTION_POOL.length);
  };

  const displayedSuggestions = [
    ...QUESTION_POOL.slice(startIndex, startIndex + 6),
    ...QUESTION_POOL.slice(0, Math.max(0, (startIndex + 6) - QUESTION_POOL.length)),
  ].slice(0, 6);

  return (
    <div className="mb-6">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center space-x-1.5 text-xs font-semibold text-slate-500 uppercase tracking-wider">
          <HelpCircle className="w-3.5 h-3.5 text-blue-700" />
          <span>Suggested HR Reports</span>
        </div>
        <button
          type="button"
          onClick={handleShuffle}
          className="flex items-center space-x-1 text-xs text-slate-500 hover:text-blue-800 transition-colors cursor-pointer"
          title="Shuffle questions"
        >
          <RefreshCw className="w-3 h-3" />
          <span>Shuffle</span>
        </button>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
        {displayedSuggestions.map((item, idx) => {
          const Icon = item.icon;
          return (
            <button
              key={idx}
              type="button"
              onClick={() => onSelectQuestion(item.label)}
              className="group text-left p-3.5 rounded-lg enterprise-card hover:bg-slate-50 transition-colors cursor-pointer flex items-start space-x-3"
            >
              <div className="p-2 rounded-md bg-blue-50 text-blue-800 group-hover:bg-blue-100 transition-colors shrink-0">
                <Icon className="w-4 h-4" />
              </div>
              <div className="min-w-0 flex-1">
                <p className="text-xs font-semibold text-slate-900 group-hover:text-blue-800 transition-colors line-clamp-1">
                  {item.label}
                </p>
                <p className="text-[11px] text-slate-500 mt-0.5">{item.desc}</p>
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
}
