from datetime import datetime, timezone

from .classify import to_signals
from .cluster import cluster_signals
from .parse import parse_feedback_input
from .synthesize import synthesize_opportunities


def analyze_feedback(payload) -> dict:
    if isinstance(payload, str):
        raw = parse_feedback_input(payload)
    else:
        raw = payload
    signals = to_signals(raw)
    clusters, unclustered = cluster_signals(signals)
    opportunities = synthesize_opportunities(clusters, signals, len(signals))
    return {
        "signals": signals,
        "opportunities": opportunities,
        "unclusteredIds": unclustered,
        "generatedAt": datetime.now(timezone.utc).isoformat(),
    }
