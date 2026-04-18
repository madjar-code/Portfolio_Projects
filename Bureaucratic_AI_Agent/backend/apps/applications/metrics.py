from prometheus_client import Counter, Histogram

applications_created_total = Counter(
    "applications_created_total",
    "Applications created (DRAFT status).",
    labelnames=["procedure"],
)

applications_submitted_total = Counter(
    "applications_submitted_total",
    "Applications submitted for AI processing.",
    labelnames=["procedure"],
)

applications_decided_total = Counter(
    "applications_decided_total",
    "Applications that received an AI decision via callback.",
    labelnames=["procedure", "decision"],
)

application_processing_duration_seconds = Histogram(
    "application_processing_duration_seconds",
    "Wall-clock seconds from submit to AI callback.",
    labelnames=["procedure", "decision"],
    buckets=(1, 5, 10, 30, 60, 120, 300, 600),
)

application_confidence_score = Histogram(
    "application_confidence_score",
    "AI confidence_score reported by the agent, per decision.",
    labelnames=["procedure", "decision"],
    buckets=(0.1, 0.3, 0.5, 0.7, 0.8, 0.9, 0.95, 0.99),
)