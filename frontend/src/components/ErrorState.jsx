import React from "react";
import { Info, AlertCircle, WifiOff } from "lucide-react";

export function ErrorState({ error }) {
  if (!error) return null;

  const errStr = String(error).toLowerCase();

  let Icon = Info;
  let title = "HR Reporting Guidance";
  let description = error;

  if (errStr.includes("unable to connect") || errStr.includes("failed to fetch")) {
    Icon = WifiOff;
    title = "Backend Service Connection Notice";
    description = "Unable to connect to the backend server. Please verify the backend API is running on http://localhost:8000.";
  } else if (errStr.includes("api key") || errStr.includes("openai_api_key")) {
    Icon = AlertCircle;
    title = "System Configuration Notice";
    description = "The OpenAI API key is missing. Please configure OPENAI_API_KEY in your environment or .env file.";
  } else if (errStr.includes("cannot be empty")) {
    Icon = Info;
    title = "Empty Query Notice";
    description = "Please enter an HR question in the search bar above.";
  }

  return (
    <div className="enterprise-card p-5 mb-6 bg-amber-50/60 border-amber-200 font-sans">
      <div className="flex items-start space-x-3">
        <div className="p-2 rounded-md bg-amber-100 text-amber-800 shrink-0">
          <Icon className="w-5 h-5" />
        </div>
        <div className="min-w-0 flex-1">
          <h4 className="text-sm font-semibold text-amber-900">{title}</h4>
          <p className="text-xs text-amber-800 leading-relaxed mt-1">{description}</p>
          
          <div className="mt-3 pt-2 border-t border-amber-200/60 text-xs text-amber-800">
            <span className="font-semibold">Supported HR Topics:</span> Active employee headcount, department breakdowns, regional leave requests, salary analytics, and open job requisitions.
          </div>
        </div>
      </div>
    </div>
  );
}
