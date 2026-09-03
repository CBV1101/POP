from __future__ import annotations

from .themes import theme_by_label


def unique(items: list) -> list:
    out = []
    for item in items:
        if item not in out:
            out.append(item)
    return out


def mode_severity(signals: list[dict]) -> str:
    counts = {"high": 0, "medium": 0, "low": 0}
    for s in signals:
        counts[s["severity"]] += 1
    if counts["high"] >= 3:
        return "high"
    if counts["high"] >= max(counts["medium"], counts["low"]) and counts["high"] > 0:
        return "high"
    if counts["medium"] >= counts["low"]:
        return "medium"
    return "low"


def frequency_band(count: int, total: int) -> str:
    share = count / max(total, 1)
    if count >= 12 or share >= 0.18:
        return "high"
    if count >= 6 or share >= 0.08:
        return "medium"
    return "low"


def confidence_of(signals: list[dict], coherence: float) -> str:
    customers = len(unique([s["customer"] for s in signals]))
    problems = sum(1 for s in signals if s["kind"] in {"problem", "mixed"})
    if len(signals) >= 12 and customers >= 8 and coherence >= 0.45 and problems >= 4:
        return "high"
    if len(signals) >= 6 and customers >= 4:
        return "medium"
    return "low"


def theme_scores(signals: list[dict]) -> list[dict]:
    counts: dict[str, int] = {}
    for s in signals:
        for t in s["themes"]:
            counts[t] = counts.get(t, 0) + 1
    return sorted(
        [{"theme": theme, "count": count} for theme, count in counts.items()],
        key=lambda x: x["count"],
        reverse=True,
    )


def pick_title(scores: list[dict], signals: list[dict]) -> str:
    labels = [s["theme"] for s in scores]
    family = {"configuration", "permissions", "documentation", "infrastructure-as-code"}
    family_hits = sum(1 for l in labels if l in family)
    if family_hits >= 2 or ("configuration" in labels and len(signals) >= 8):
        return "Reduce initial integration complexity"
    if scores:
        definition = theme_by_label(scores[0]["theme"])
        if definition:
            return definition["problem_title"]
    problem = next((s for s in signals if s["kind"] == "problem"), None)
    if problem:
        words = " ".join(problem["text"].split()[:8])
        return f"Investigate: {words}"
    return "Unnamed customer problem"


def interpretation(title: str, signals: list[dict], scores: list[dict]) -> str:
    solution_n = sum(1 for s in signals if s["kind"] == "solution_request")
    problem_n = sum(1 for s in signals if s["kind"] in {"problem", "mixed"})
    themes = [s["theme"] for s in scores[:4]]
    theme_list = ", ".join(themes) if themes else "the same workflow"
    customers = len(unique([s["customer"] for s in signals]))
    if title == "Reduce initial integration complexity":
        return (
            f"Customers are proposing different solutions, but the underlying problem appears "
            f"to be difficulty configuring the product correctly during initial integration. "
            f"Across {customers} accounts, the same job-to-be-done keeps showing up as {theme_list}. "
            f"Requested fixes (Terraform, better docs, permission lists) are downstream of that "
            f"setup pain, not independent bets."
        )
    if solution_n > problem_n:
        return (
            f"This cluster is heavy on requested solutions ({solution_n} of {len(signals)} signals). "
            f"Treating those requests as the spec would overfit to one implementation. The shared pain "
            f"is {title.lower()}, evidenced across {customers} customers around {theme_list}."
        )
    return (
        f"{problem_n} signals describe a live problem; {solution_n} propose a particular fix. "
        f"The recurring issue is {title.lower()}, with common themes: {theme_list}."
    )


def solutions_for(title: str, scores: list[dict], signals: list[dict]) -> list[str]:
    if title == "Reduce initial integration complexity":
        from_theme = []
        for label in ("configuration", "permissions", "documentation", "infrastructure-as-code"):
            definition = theme_by_label(label)
            if definition:
                from_theme.extend(definition["solutions"])
    elif scores:
        definition = theme_by_label(scores[0]["theme"])
        from_theme = list(definition["solutions"]) if definition else []
    else:
        from_theme = []
    from_signals = [
        item
        for s in signals
        for item in s["requestedSolutions"]
        if item[:1].isupper() and len(item) > 18
    ]
    merged = unique([s for s in from_theme + from_signals if len(s) > 4])
    return merged[:5]


def problem_vs_solution_note(signals: list[dict]) -> str:
    problems = sum(1 for s in signals if s["kind"] == "problem")
    solutions = sum(1 for s in signals if s["kind"] == "solution_request")
    mixed = sum(1 for s in signals if s["kind"] == "mixed")
    return (
        f"{problems} problem statements, {solutions} solution requests, {mixed} mixed. "
        f"Rank the problem, not the loudest request."
    )


def importance_score(signal_count: int, customer_count: int, enterprise_count: int, severity: str, frequency: str) -> int:
    sev = {"high": 1, "medium": 0.62, "low": 0.32}[severity]
    freq = {"high": 1, "medium": 0.65, "low": 0.35}[frequency]
    return round(
        100
        * (
            0.34 * min(signal_count / 24, 1)
            + 0.28 * min(customer_count / 12, 1)
            + 0.18 * min(enterprise_count / 7, 1)
            + 0.12 * sev
            + 0.08 * freq
        )
    )


def opportunity_from_members(opp_id: str, members: list[dict], total_signals: int) -> dict:
    scores = theme_scores(members)
    title = pick_title(scores, members)
    customers = unique([s["customer"] for s in members])
    enterprise_count = len(unique([s["customer"] for s in members if s["segment"] == "enterprise"]))
    severity = mode_severity(members)
    frequency = frequency_band(len(members), total_signals)
    top_share = scores[0]["count"] / len(members) if scores else 0
    return {
        "id": opp_id,
        "title": title,
        "interpretation": interpretation(title, members, scores),
        "potentialSolutions": solutions_for(title, scores, members),
        "themes": scores,
        "signalIds": [s["id"] for s in members],
        "customerCount": len(customers),
        "enterpriseCount": enterprise_count,
        "signalCount": len(members),
        "problemCount": sum(1 for s in members if s["kind"] in {"problem", "mixed"}),
        "solutionRequestCount": sum(1 for s in members if s["kind"] == "solution_request"),
        "frequency": frequency,
        "severity": severity,
        "importance": importance_score(
            len(members), len(customers), enterprise_count, severity, frequency
        ),
        "confidence": confidence_of(members, top_share),
        "problemVsSolutionNote": problem_vs_solution_note(members),
    }


def synthesize_opportunities(clusters: list[dict], signals: list[dict], total_signals: int) -> list[dict]:
    by_id = {s["id"]: s for s in signals}
    grouped: dict[str, list[str]] = {}
    order: list[str] = []
    for cluster in clusters:
        members = [by_id[sid] for sid in cluster["signalIds"] if sid in by_id]
        title = pick_title(theme_scores(members), members)
        if title not in grouped:
            grouped[title] = []
            order.append(title)
        grouped[title].extend(cluster["signalIds"])
    opportunities = []
    for index, title in enumerate(order, start=1):
        ids = unique(grouped[title])
        members = [by_id[sid] for sid in ids if sid in by_id]
        opportunities.append(opportunity_from_members(f"OPP-{index:02d}", members, total_signals))
    opportunities.sort(key=lambda o: o["importance"], reverse=True)
    for index, opp in enumerate(opportunities, start=1):
        opp["id"] = f"OPP-{index:02d}"
    return opportunities
