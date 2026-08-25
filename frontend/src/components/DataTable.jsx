import React, { useState } from "react";
import { Table, Search, Download, FileSpreadsheet } from "lucide-react";
import { formatColumnHeader, formatCellValue } from "../utils/formatData";

export function DataTable({ data, truncated }) {
  const [searchTerm, setSearchTerm] = useState("");

  if (!data || !Array.isArray(data) || data.length === 0) {
    return null;
  }

  const columns = Object.keys(data[0]);

  // Filter rows based on search term
  const filteredData = data.filter((row) =>
    columns.some((col) =>
      String(row[col] ?? "")
        .toLowerCase()
        .includes(searchTerm.toLowerCase())
    )
  );

  // CSV Export Handler
  const exportToCSV = () => {
    if (!data || data.length === 0) return;

    const headers = columns.map(formatColumnHeader).join(",");
    const rows = data.map((row) =>
      columns
        .map((col) => {
          const val = row[col];
          if (val === null || val === undefined) return '""';
          const stringVal = String(val).replace(/"/g, '""');
          return `"${stringVal}"`;
        })
        .join(",")
    );

    const csvContent = "data:text/csv;charset=utf-8," + [headers, ...rows].join("\n");
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", `HR_Analytics_Export_${new Date().toISOString().slice(0, 10)}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="enterprise-card overflow-hidden mb-6 bg-white font-sans">
      {/* Header Bar with Title, Search & Prominent Export Button */}
      <div className="p-4 bg-slate-50 border-b border-slate-200 flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center space-x-2">
          <Table className="w-4 h-4 text-blue-700" />
          <h3 className="text-sm font-semibold text-slate-800">Structured Data Results</h3>
          <span className="text-xs px-2 py-0.5 rounded bg-slate-200 text-slate-700 font-medium">
            {filteredData.length} {filteredData.length === 1 ? "row" : "rows"}
          </span>
        </div>

        <div className="flex items-center space-x-3">
          {/* Inline Search Input */}
          <div className="relative">
            <Search className="w-3.5 h-3.5 text-slate-400 absolute left-2.5 top-2.5" />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search table rows..."
              className="pl-8 pr-3 py-1.5 bg-white border border-slate-300 rounded-md text-xs text-slate-800 placeholder-slate-400 focus:outline-none focus:border-blue-600 focus:ring-1 focus:ring-blue-600 w-44 sm:w-56"
            />
          </div>

          {/* Prominent Export to Excel/CSV Button */}
          <button
            type="button"
            onClick={exportToCSV}
            className="inline-flex items-center space-x-1.5 px-3 py-1.5 bg-emerald-700 hover:bg-emerald-800 text-white rounded-md text-xs font-medium shadow-sm transition-colors cursor-pointer"
          >
            <FileSpreadsheet className="w-3.5 h-3.5 text-white" />
            <span>Export to Excel / CSV</span>
          </button>
        </div>
      </div>

      {/* Truncated Notice */}
      {truncated && (
        <div className="px-4 py-2 bg-amber-50 border-b border-amber-200 text-amber-800 text-xs flex items-center space-x-2">
          <Download className="w-3.5 h-3.5 text-amber-600 shrink-0" />
          <span>Results truncated to 100 rows for display performance. Export to CSV to view full data.</span>
        </div>
      )}

      {/* Table Container */}
      <div className="overflow-x-auto max-h-[450px]">
        <table className="w-full text-left text-xs text-slate-800">
          <thead className="bg-slate-100 text-slate-700 font-semibold border-b border-slate-200 sticky top-0 z-10">
            <tr>
              {columns.map((col) => (
                <th key={col} className="px-4 py-2.5 whitespace-nowrap">
                  {formatColumnHeader(col)}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-200">
            {filteredData.length > 0 ? (
              filteredData.map((row, rowIdx) => (
                <tr
                  key={rowIdx}
                  className="hover:bg-blue-50/40 transition-colors duration-100 even:bg-slate-50/50"
                >
                  {columns.map((col) => (
                    <td key={col} className="px-4 py-2.5 whitespace-nowrap font-medium text-slate-800">
                      {formatCellValue(row[col], col)}
                    </td>
                  ))}
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan={columns.length} className="px-4 py-8 text-center text-slate-500 italic">
                  No matching rows found for "{searchTerm}".
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
