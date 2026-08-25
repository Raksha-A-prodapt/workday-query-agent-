/**
 * Utilities for formatting column headers and cell values in data tables.
 */

export function formatColumnHeader(key) {
  if (!key) return "";
  return key
    .replace(/_/g, " ")
    .replace(/\b\w/g, (char) => char.toUpperCase());
}

export function formatCellValue(value, colName = "") {
  if (value === null || value === undefined) {
    return "null";
  }

  // Format currency for salary or budget columns
  const lowerCol = colName.toLowerCase();
  if ((lowerCol.includes("salary") || lowerCol.includes("budget") || lowerCol.includes("payroll")) && typeof value === "number") {
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "USD",
      maximumFractionDigits: 2,
    }).format(value);
  }

  // Format numeric values with commas
  if (typeof value === "number" && Number.isInteger(value)) {
    return new Intl.NumberFormat("en-US").format(value);
  }

  // Format float decimals
  if (typeof value === "number") {
    return new Intl.NumberFormat("en-US", { maximumFractionDigits: 2 }).format(value);
  }

  return String(value);
}
