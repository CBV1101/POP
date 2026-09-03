from __future__ import annotations

from .classify import to_signals
from .cluster import cluster_signals
from .parse import parse_feedback_input
from .synthesize import unique

PRIMITIVES = [
    {
        "id": "config-spec",
        "covers": ["configuration", "permissions", "documentation", "infrastructure-as-code"],
        "title": "Validated configuration spec",
        "one_liner": "One machine-readable description of a working setup that can be checked, shown, and applied.",
        "smallest_build": [
            "A schema for the setup (environment, scopes, webhooks, credentials)",
            "A validate endpoint that reports missing permissions and drift from live API behavior",
            "JSON export of a valid spec so UI, CLI, and Terraform are clients—not separate products",
        ],
        "defer": [
            "A full Terraform/Pulumi provider (generate it later from the spec)",
            "A conversational setup assistant",
            "Hand-rewriting every docs page",
        ],
    },
    {
        "id": "query-model",
        "covers": ["search"],
        "title": "One query model",
        "one_liner": "A single way to ask for records, with filters as part of the query—not extra screens.",
        "smallest_build": [
            "A query object (text, filters, sort) that the API and UI both use",
            "Stable ranking and match rules, including renamed records",
            "Save/replay of that query object",
        ],
        "defer": [
            "A new search engine brand",
            "Natural-language parsing as a separate product",
        ],
    },
    {
        "id": "event-router",
        "covers": ["notifications"],
        "title": "Severity-based event router",
        "one_liner": "Events with a severity, and a default quiet path. Everything else is a destination.",
        "smallest_build": [
            "An event stream with severity and object id",
            "A default digest; critical events bypass it",
            "Mute and route as rules on that stream",
        ],
        "defer": [
            "A new notification product surface",
            "Per-comment email as the default",
        ],
    },
    {
        "id": "directory-sync",
        "covers": ["identity"],
        "title": "Directory as source of truth",
        "one_liner": "Membership and roles come from the identity provider, not from this product’s user table.",
        "smallest_build": [
            "Group-to-role mapping",
            "Deprovision when the IdP says so",
            "SCIM or JIT from the same mapping",
        ],
        "defer": [
            "Custom SSO screens per customer",
            "Manual seat management for enterprise",
        ],
    },
    {
        "id": "usage-ledger",
        "covers": ["billing"],
        "title": "Usage ledger",
        "one_liner": "One ledger of billable events that invoices, alerts, and the usage page all read.",
        "smallest_build": [
            "Append-only usage records with team, unit, and timestamp",
            "Invoice lines generated from the ledger",
            "A forecast from the same records",
        ],
        "defer": [
            "A new pricing page",
            "One-off invoice explanations in support",
        ],
    },
    {
        "id": "idempotent-writes",
        "covers": ["reliability"],
        "title": "Idempotent writes",
        "one_liner": "Clients can retry safely. Failures are named, not silent.",
        "smallest_build": [
            "Idempotency keys on write endpoints",
            "Error bodies that say what to do next",
            "A public signal when you are degraded",
        ],
        "defer": [
            "Raising rate limits as the only fix",
            "A status page as a substitute for retries",
        ],
    },
    {
        "id": "customer-owned-export",
        "covers": ["export"],
        "title": "Customer-owned export",
        "one_liner": "Their data leaves in a file they can schedule. Warehouse sync is a client of that file.",
        "smallest_build": [
            "A complete export job (CSV or JSON) including audit events",
            "A schedule or download",
        ],
        "defer": [
            "A native Snowflake connector as the first build",
            "Per-platform export UIs",
        ],
    },
]


def best_primitive(signal: dict) -> dict | None:
    themes = set(signal.get("themes") or [])
    if not themes:
        return None
    scored = []
    for primitive in PRIMITIVES:
        overlap = len(themes & set(primitive["covers"]))
        if overlap:
            scored.append((overlap, -len(primitive["covers"]), primitive))
    if not scored:
        return None
    scored.sort(reverse=True)
    return scored[0][2]


def how_covers(signal: dict, primitive: dict) -> str:
    themes = set(signal.get("themes") or [])
    text = signal["text"].lower()
    pid = primitive["id"]
    if pid == "config-spec":
        if "infrastructure-as-code" in themes or "terraform" in text or "pulumi" in text:
            return "IaC applies the spec. You do not need a one-off Terraform product first."
        if "permissions" in themes:
            return "Validate reads the spec and lists missing scopes before go-live."
        if "documentation" in themes:
            return "If the spec and the API disagree, validation fails. Docs can follow the spec."
        if "wizard" in text or "assistant" in text or "guided" in text:
            return "The wizard writes the spec. It is a client, not the source of truth."
        return "This is another way to create or inspect the same spec."
    if pid == "query-model":
        if "saved" in text:
            return "Saving is storing the query object."
        if "natural" in text or "elasticsearch" in text:
            return "Language or engine choice sits on the same query object."
        return "This is a client of one query model, not a new search product."
    if pid == "event-router":
        return "A destination or mute rule on the same event stream."
    if pid == "directory-sync":
        return "A way to read membership from the IdP into one mapping."
    if pid == "usage-ledger":
        return "A read of the same ledger (invoice, alert, or breakdown)."
    if pid == "idempotent-writes":
        return "Safe retry or a clearer failure on the same write path."
    if pid == "customer-owned-export":
        return "A consumer of the same export job."
    return "Covered by the same primitive."


def _from_playbook(primitive: dict, members: list[dict], total: int) -> dict:
    coverage = [
        {
            "id": s["id"],
            "text": s["text"],
            "customer": s["customer"],
            "how": how_covers(s, primitive),
        }
        for s in members
    ]
    return {
        "id": primitive["id"],
        "title": primitive["title"],
        "oneLiner": primitive["one_liner"],
        "smallestBuild": primitive["smallest_build"],
        "defer": primitive["defer"],
        "requestCount": len(members),
        "totalRequests": total,
        "coverage": coverage,
        "playbook": True,
    }


def _from_cluster(cluster_id: str, members: list[dict], total: int) -> dict:
    title_src = members[0]["text"]
    words = " ".join(title_src.split()[:8]).rstrip(".")
    return {
        "id": cluster_id,
        "title": f"Shared capability: {words}",
        "oneLiner": "These asks look related, but they are not a known product primitive. Ship the shared job once.",
        "smallestBuild": [
            "Name the job these requests share",
            "Build one interface for that job",
            "Treat each request as a client of that interface",
        ],
        "defer": ["Building every requested UI as its own project"],
        "requestCount": len(members),
        "totalRequests": total,
        "coverage": [
            {
                "id": s["id"],
                "text": s["text"],
                "customer": s["customer"],
                "how": "Treat as a variant of the same job, not a separate roadmap item.",
            }
            for s in members
        ],
        "playbook": False,
    }


def find_primitives(payload) -> dict:
    raw = parse_feedback_input(payload) if isinstance(payload, str) else payload
    signals = to_signals(raw)
    buckets: dict[str, list] = {p["id"]: [] for p in PRIMITIVES}
    leftover: list[dict] = []
    by_id = {p["id"]: p for p in PRIMITIVES}

    for signal in signals:
        match = best_primitive(signal)
        if match:
            buckets[match["id"]].append(signal)
        else:
            leftover.append(signal)

    primitives = []
    for primitive in PRIMITIVES:
        members = buckets[primitive["id"]]
        if members:
            primitives.append(_from_playbook(primitive, members, len(signals)))

    if leftover:
        clusters, singles = cluster_signals(leftover)
        leftover_by_id = {s["id"]: s for s in leftover}
        for cluster in clusters:
            members = [leftover_by_id[i] for i in cluster["signalIds"] if i in leftover_by_id]
            if members:
                primitives.append(_from_cluster(cluster["id"], members, len(signals)))
        uncovered = [leftover_by_id[i] for i in singles if i in leftover_by_id]
    else:
        uncovered = []

    primitives.sort(key=lambda p: p["requestCount"], reverse=True)
    covered = sum(p["requestCount"] for p in primitives)
    if not primitives:
        summary = "No shared primitive yet. Add more related requests."
    elif len(primitives) == 1:
        summary = (
            f"One primitive covers {primitives[0]['requestCount']} of {len(signals)} requests. "
            f"Build that, not each ask."
        )
    else:
        summary = (
            f"These are {len(primitives)} separate primitives, not one feature. "
            f"Together they cover {covered} of {len(signals)} requests. Don’t merge them."
        )

    return {
        "kind": "primitives",
        "summary": summary,
        "requests": signals,
        "primitives": primitives,
        "uncovered": [{"id": s["id"], "text": s["text"]} for s in uncovered],
        "generatedAt": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(),
    }
