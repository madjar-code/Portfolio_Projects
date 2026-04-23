import type { AIReport, ValidationIssue } from '../../types/applications'

export default function AIReportPanel({ report }: { report: AIReport }) {
  return (
    <div className="bg-white border rounded-lg p-6 space-y-4">
      <h2 className="text-lg font-semibold">AI Report</h2>

      <div className="flex items-center gap-3">
        <span className={`text-sm font-medium px-2 py-0.5 rounded ${
          report.decision === 'ACCEPT' ? 'bg-green-100 text-green-700' :
          report.decision === 'REJECT' ? 'bg-red-100 text-red-700' :
          'bg-gray-100 text-gray-700'
        }`}>
          {report.decision}
        </span>
        <span className="text-sm text-gray-500">
          Confidence: {Math.round(report.confidence_score * 100)}%
        </span>
      </div>

      {report.issues_found.length > 0 && (
        <div>
          <h3 className="text-sm font-medium text-gray-700 mb-2">Issues</h3>
          <ul className="space-y-1">
            {report.issues_found.map((issue: ValidationIssue, i: number) => (
              <li key={i} className="text-sm text-gray-600">
                <span className="font-medium">{issue.field}:</span> {issue.detail}
              </li>
            ))}
          </ul>
        </div>
      )}

      {report.recommendations && (
        <div>
          <h3 className="text-sm font-medium text-gray-700 mb-1">Recommendations</h3>
          <p className="text-sm text-gray-600">{report.recommendations}</p>
        </div>
      )}

      <p className="text-xs text-gray-400">
        Model: {report.ai_model_used} · Prompt: {report.prompt_version} · {report.processing_time_seconds}s
      </p>
    </div>
  )
}