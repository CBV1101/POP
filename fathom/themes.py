import re

THEMES = [
    {
        "id": "integration-setup",
        "label": "configuration",
        "keywords": [
            "setup",
            "set up",
            "onboard",
            "onboarding",
            "implement",
            "implementation",
            "configure",
            "configuration",
            "integrate",
            "integration",
            "sdk",
            "install",
            "getting started",
            "time to value",
            "two weeks",
            "took our developer",
        ],
        "problem_title": "Reduce initial integration complexity",
        "solutions": [
            "Guided configuration",
            "AI integration assistant",
            "Configuration validation API",
            "Starter templates for common stacks",
        ],
    },
    {
        "id": "permissions",
        "label": "permissions",
        "keywords": [
            "permission",
            "permissions",
            "iam",
            "roles",
            "rbac",
            "scopes",
            "access denied",
            "unauthorized",
            "403",
            "least privilege",
        ],
        "problem_title": "Make required permissions discoverable",
        "solutions": [
            "Improved permission diagnostics",
            "Least-privilege permission catalog",
            "Preflight access checker",
        ],
    },
    {
        "id": "docs",
        "label": "documentation",
        "keywords": [
            "docs",
            "documentation",
            "readme",
            "tutorial",
            "mismatch",
            "docs say",
            "documentation",
            "docs",
            "outdated docs",
            "getting-started",
        ],
        "problem_title": "Close the gap between docs and actual API behavior",
        "solutions": [
            "Docs generated from live API contracts",
            "Worked examples for the happy path and failure modes",
            "In-product setup checklist",
        ],
    },
    {
        "id": "iac",
        "label": "infrastructure-as-code",
        "keywords": [
            "terraform",
            "pulumi",
            "cloudformation",
            "helm",
            "iac",
            "infra as code",
            "provider",
        ],
        "problem_title": "Support infrastructure-as-code provisioning",
        "solutions": [
            "Official Terraform provider",
            "Pulumi module",
            "Exportable configuration as code",
        ],
    },
    {
        "id": "search",
        "label": "search",
        "keywords": [
            "search",
            "can't find",
            "cannot find",
            "couldn't find",
            "findability",
            "saved search",
            "filter",
            "filters",
        ],
        "problem_title": "Make it faster to find the right records",
        "solutions": ["Relevance ranking over recency", "Saved filters", "Natural-language search"],
    },
    {
        "id": "billing",
        "label": "billing",
        "keywords": [
            "invoice",
            "billing",
            "charge",
            "overage",
            "pricing",
            "seat",
            "usage",
            "unexpected bill",
        ],
        "problem_title": "Make usage and billing predictable",
        "solutions": [
            "Usage forecast and alerts",
            "Invoice line-item explanations",
            "Seat vs usage breakdown in-product",
        ],
    },
    {
        "id": "notifications",
        "label": "notifications",
        "keywords": [
            "notification",
            "notifications",
            "email",
            "emails",
            "too many emails",
            "alert",
            "noisy",
            "digest",
        ],
        "problem_title": "Reduce notification noise without missing critical events",
        "solutions": ["Smart digest by default", "Per-event mute controls", "Severity-based routing"],
    },
    {
        "id": "identity",
        "label": "identity",
        "keywords": ["sso", "saml", "scim", "okta", "azure ad", "entra", "provisioning"],
        "problem_title": "Complete enterprise identity and provisioning",
        "solutions": [
            "SCIM directory sync",
            "Just-in-time SSO provisioning",
            "Group-to-role mapping UI",
        ],
    },
    {
        "id": "reliability",
        "label": "reliability",
        "keywords": ["timeout", "outage", "500", "latency", "slow api", "rate limit", "retry"],
        "problem_title": "Improve API reliability under load",
        "solutions": [
            "Idempotent retries with clearer errors",
            "Status page for partial degradation",
            "Raised rate limits for enterprise",
        ],
    },
    {
        "id": "export",
        "label": "export",
        "keywords": ["export", "csv", "download", "audit log", "compliance"],
        "problem_title": "Give customers durable exports of their own data",
        "solutions": ["Scheduled CSV/JSON exports", "Audit log download", "Warehouse sync"],
    },
]


def _has_keyword(text: str, keyword: str) -> bool:
    if " " in keyword or "-" in keyword:
        return keyword in text
    return re.search(r"\b" + re.escape(keyword) + r"\b", text) is not None


def match_themes(text: str):
    lower = text.lower()
    return [theme["label"] for theme in THEMES if any(_has_keyword(lower, kw) for kw in theme["keywords"])]


def theme_by_label(label: str):
    for theme in THEMES:
        if theme["label"] == label:
            return theme
    return None
