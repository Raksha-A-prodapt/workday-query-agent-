/**
 * Helper utility to analyze data rows and auto-detect whether KPI stat card,
 * Recharts BarChart, or plain table format is appropriate.
 * Features smart automatic aggregation for detailed record lists containing category fields.
 */

export function detectChartType(data) {
  if (!data || !Array.isArray(data) || data.length === 0) {
    return { type: "none" };
  }

  const sampleRow = data[0];
  const keys = Object.keys(sampleRow);

  // Single row results (e.g. active headcount total = 425)
  if (data.length === 1) {
    const numKey = keys.find((k) => typeof sampleRow[k] === "number") || keys[0];
    return {
      type: "kpi",
      label: numKey,
      value: sampleRow[numKey],
      raw: sampleRow,
    };
  }

  // Multiple row results
  if (data.length > 1) {
    let catKey = keys.find((k) => typeof sampleRow[k] === "string");
    let numKey = keys.find((k) => typeof sampleRow[k] === "number");

    if (!catKey) catKey = keys[0];

    // Case A: Pre-aggregated numeric column present (e.g. headcount, avg_salary)
    if (catKey && numKey && typeof sampleRow[numKey] === "number") {
      const isCurrency =
        numKey.toLowerCase().includes("salary") ||
        numKey.toLowerCase().includes("budget") ||
        numKey.toLowerCase().includes("pay");

      return {
        type: "bar",
        catKey,
        numKey,
        isCurrency,
        chartData: data,
      };
    }

    // Case B: Detailed individual record list (e.g. 50 employees on leave) with department/region column
    const categoryKey = keys.find(
      (k) => k.toLowerCase().includes("department") || k.toLowerCase().includes("region") || k.toLowerCase().includes("status")
    );

    if (categoryKey) {
      const counts = {};
      data.forEach((row) => {
        const val = String(row[categoryKey] || "Other");
        counts[val] = (counts[val] || 0) + 1;
      });

      const aggregatedRows = Object.keys(counts).map((cat) => ({
        [categoryKey]: cat,
        employee_count: counts[cat],
      }));

      return {
        type: "bar",
        catKey: categoryKey,
        numKey: "employee_count",
        isCurrency: false,
        chartData: aggregatedRows,
      };
    }
  }

  return { type: "none" };
}
