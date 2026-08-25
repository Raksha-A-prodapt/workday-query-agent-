import React from "react";
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Cell,
} from "recharts";
import { BarChart3 } from "lucide-react";
import { detectChartType } from "../utils/chartDetector";
import { formatColumnHeader, formatCellValue } from "../utils/formatData";
import { KpiStatCard } from "./KpiStatCard";

const BAR_COLORS = [
  "#1e40af", // Corporate Blue
  "#2563eb", 
  "#3b82f6", 
  "#1d4ed8", 
  "#0284c7", 
  "#0f766e", 
  "#4338ca", 
  "#0369a1", 
];

export function ChartRenderer({ data }) {
  const info = detectChartType(data);

  if (info.type === "kpi") {
    return <KpiStatCard label={info.label} value={info.value} />;
  }

  if (info.type !== "bar") {
    return null;
  }

  const { catKey, numKey, isCurrency, chartData } = info;
  const activeData = chartData || data;

  // Custom Recharts Tooltip for Enterprise Light Theme
  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      const val = payload[0].value;
      return (
        <div className="bg-white px-3 py-2 rounded-lg border border-slate-200 shadow-md text-xs font-sans">
          <p className="font-semibold text-slate-900">{label}</p>
          <p className="text-blue-800 font-medium mt-0.5">
            {formatColumnHeader(numKey)}: {formatCellValue(val, numKey)}
          </p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="enterprise-card p-6 mb-6 bg-white font-sans">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-2">
          <BarChart3 className="w-4 h-4 text-blue-800" />
          <h3 className="text-sm font-semibold text-slate-900">
            Analytics Breakdown: {formatColumnHeader(numKey)} by {formatColumnHeader(catKey)}
          </h3>
        </div>
        <span className="text-xs px-2 py-0.5 rounded bg-slate-100 text-slate-600 font-medium">
          Column Chart
        </span>
      </div>

      <div className="h-72 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={activeData} margin={{ top: 10, right: 10, left: 10, bottom: 25 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" vertical={false} />
            <XAxis
              dataKey={catKey}
              stroke="#64748b"
              fontSize={11}
              tickLine={false}
              axisLine={{ stroke: "#cbd5e1" }}
              interval={0}
              angle={-15}
              textAnchor="end"
            />
            <YAxis
              stroke="#64748b"
              fontSize={11}
              tickLine={false}
              axisLine={false}
              tickFormatter={(v) => (isCurrency ? `$${v >= 1000 ? `${(v / 1000).toFixed(0)}k` : v}` : v)}
            />
            <Tooltip content={<CustomTooltip />} cursor={{ fill: "#f1f5f9" }} />
            <Bar dataKey={numKey} radius={[4, 4, 0, 0]}>
              {activeData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={BAR_COLORS[index % BAR_COLORS.length]} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
