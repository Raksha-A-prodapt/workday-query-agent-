import React from "react";
import { Header } from "./components/Header";
import { QueryInput } from "./components/QueryInput";
import { SuggestedQuestions } from "./components/SuggestedQuestions";
import { QueryHistory } from "./components/QueryHistory";
import { LoadingSteps } from "./components/LoadingSteps";
import { AnswerCard } from "./components/AnswerCard";
import { ChartRenderer } from "./components/ChartRenderer";
import { DataTable } from "./components/DataTable";
import { SqlViewer } from "./components/SqlViewer";
import { EmptyState } from "./components/EmptyState";
import { ErrorState } from "./components/ErrorState";
import { useQuery } from "./hooks/useQuery";
import { useHistory } from "./hooks/useHistory";

export default function App() {
  const {
    question,
    inputQuestion,
    setInputQuestion,
    loading,
    stepIndex,
    result,
    error,
    submitQuery,
  } = useQuery();

  const { history, addHistory, clearHistory } = useHistory();

  const handleRunQuery = (queryText) => {
    setInputQuestion(queryText);
    submitQuery(queryText);
    addHistory(queryText);
  };

  return (
    <div className="min-h-screen bg-[#FAFBFC] text-slate-900 flex flex-col font-sans selection:bg-blue-100 selection:text-blue-900">
      {/* Header */}
      <Header />

      {/* Main Container */}
      <main className="flex-1 max-w-5xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        
        {/* Title Banner */}
        <div className="text-center max-w-xl mx-auto mb-6">
          <h2 className="text-2xl font-bold text-slate-900 tracking-tight sm:text-3xl">
            Workday HR Analytics AI Assistant
          </h2>
          <p className="mt-1.5 text-xs text-slate-600">
            Ask natural-language questions to query employee headcount, department budgets, leave balances, and open job requisitions.
          </p>
        </div>

        {/* Natural Language Query Input */}
        <QueryInput
          value={inputQuestion}
          onChange={setInputQuestion}
          onSubmit={() => handleRunQuery(inputQuestion)}
          loading={loading}
        />

        {/* Recent Query Thread */}
        <QueryHistory
          history={history}
          onSelectQuestion={handleRunQuery}
          onClearHistory={clearHistory}
        />

        {/* Suggested Questions Grid */}
        <SuggestedQuestions onSelectQuestion={handleRunQuery} />

        {/* Loading Progress Indicator */}
        {loading && <LoadingSteps currentStepIndex={stepIndex} />}

        {/* Error / System Guidance Banner */}
        {error && <ErrorState error={error} />}

        {/* Output Results Container */}
        {result && !loading && (
          <div className="space-y-6">
            {/* Answer Card with Compliance Verification Line */}
            <AnswerCard
              answer={result.answer}
              rowCount={result.row_count}
              error={result.error}
              status={result.status}
            />

            {/* Auto-detected Analytics Visualization / KPI */}
            <ChartRenderer data={result.data} />

            {/* Dynamic Data Table with Excel / CSV Export */}
            <DataTable data={result.data} truncated={result.truncated} />

            {/* De-emphasized Collapsible SQL Audit Code Block */}
            <SqlViewer sql={result.generated_sql} />
          </div>
        )}

        {/* Initial Empty State */}
        {!result && !loading && !error && <EmptyState />}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-200 py-6 text-center text-xs text-slate-500 font-sans">
        Workday HR Analytics Assistant • Read-Only SQLite Compliance Agent
      </footer>
    </div>
  );
}
