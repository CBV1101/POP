from __future__ import annotations

from datetime import datetime, timezone

LEVELS = {"none": 0.0, "low": 0.33, "medium": 0.67, "high": 1.0}
WORK = {
    "feature": {"label": "Feature", "must": False, "rank": 0},
    "ktlo": {"label": "Lights on", "must": True, "rank": 1},
    "reliability": {"label": "Reliability", "must": True, "rank": 2},
    "compliance": {"label": "Legal / compliance", "must": True, "rank": 3},
    "security": {"label": "Security patch", "must": True, "rank": 4},
}


def _num(value, default=0.0) -> float:
    try:
        if value is None or value == "":
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def _norm(values: list[float]) -> list[float]:
    peak = max(values) if values else 0
    if peak <= 0:
        return [0.0 for _ in values]
    return [v / peak for v in values]


def _reason_bits(item: dict, rice: float, drivers: list[tuple[str, float]]) -> list[str]:
    bits = []
    for name, _, _ in drivers[:3]:
        if name == "RICE" and rice > 0:
            bits.append(f"RICE {round(rice, 1)}")
        elif name == "Revenue / effort" and _num(item.get("revenue")):
            bits.append(f"${int(_num(item.get('revenue'))):,} revenue vs {item.get('effort') or 0:g} days")
        elif name == "ROI" and _num(item.get("roi")):
            bits.append(f"{_num(item.get('roi')):g}× ROI")
        elif name == "Go / no-go" and _num(item.get("dealValue")):
            bits.append(f"Go/no-go deal ${int(_num(item.get('dealValue'))):,}")
        elif name == "Churn if skipped" and _num(item.get("churnArr")):
            bits.append(f"${int(_num(item.get('churnArr'))):,} churn risk if skipped")
        elif name == "Debt":
            added = item.get("debtAdded") or "none"
            reduced = item.get("debtReduced") or "none"
            bits.append(f"Debt added {added}, reduced {reduced}")
        elif name == "Urgency":
            flags = []
            if item.get("blocksOthers"):
                flags.append("blocks other work")
            if item.get("compliance"):
                flags.append("compliance")
            if item.get("timeSensitive"):
                flags.append("time-sensitive window")
            if flags:
                bits.append(", ".join(flags))
    if item.get("must"):
        bits.insert(0, f"{item.get('workLabel') or 'Must-do'} — ships before feature work")
    if item.get("deal") in {"signup", "expansion"} and _num(item.get("dealValue")):
        kind = "signs up" if item.get("deal") == "signup" else "expands"
        bits.append(f"Customer {kind} if this ships")
    return unique(bits)[:4]


def unique(items: list) -> list:
    out = []
    for item in items:
        if item and item not in out:
            out.append(item)
    return out


def _order_why(item: dict, role: str, room: float, wave: int, anchor: dict | None = None) -> str:
    if role == "blocked":
        return f"Wait — this takes {item['loadPct']:g}% of the team and only {room:g}% is free."
    if role == "side" and anchor:
        return (
            f"Run with {anchor['title']}: leftover team capacity, and {item['effort']:g} days "
            f"finishes no later than that job."
        )
    if item.get("must"):
        reason = f"{item.get('workLabel') or 'Required work'} — it has to ship"
    elif item.get("deal") != "none" and _num(item.get("dealValue")):
        reason = "A customer deal depends on this"
    elif (item.get("churn") or "none") in {"high", "medium"}:
        reason = "Skipping it risks churn"
    else:
        reason = f"Highest remaining RICE ({item.get('rice')})"
    if wave == 1:
        return f"{reason}. Start now while {room:g}% of the team is free."
    return f"{reason}. Next after the previous wave finishes."


def prioritize(payload: dict) -> dict:
    items = payload.get("items") or []
    if not items:
        raise RuntimeError("Add backlog items to rank.")

    scored = []
    for index, raw in enumerate(items):
        title = (raw.get("title") or raw.get("text") or "").strip()
        if not title:
            continue
        effort = max(_num(raw.get("effort"), 5), 0.25)
        reach = _num(raw.get("reach"), 0)
        impact = _num(raw.get("impact"), 1)
        confidence = min(max(_num(raw.get("confidence"), 50), 0), 100) / 100
        rice = reach * impact * confidence / effort
        revenue = _num(raw.get("revenue"))
        roi = _num(raw.get("roi"))
        deal_value = _num(raw.get("dealValue")) if (raw.get("deal") or "none") != "none" else 0
        churn = _num(raw.get("churnArr")) * LEVELS.get(raw.get("churn") or "none", 0)
        debt = LEVELS.get(raw.get("debtReduced") or "none", 0) - LEVELS.get(raw.get("debtAdded") or "none", 0)
        urgency = 0.0
        if raw.get("blocksOthers"):
            urgency += 0.45
        if raw.get("compliance"):
            urgency += 0.35
        if raw.get("timeSensitive"):
            urgency += 0.35
        if raw.get("blockedBy"):
            urgency -= 0.25
        work_type = (raw.get("workType") or "feature").strip().lower()
        if work_type not in WORK:
            work_type = "feature"
        work = WORK[work_type]
        scored.append(
            {
                "id": raw.get("id") or f"BL-{index + 1:02d}",
                "title": title,
                "workType": work_type,
                "workLabel": work["label"],
                "must": work["must"],
                "mustRank": work["rank"],
                "effort": effort,
                "reach": reach,
                "impact": impact,
                "confidence": confidence * 100,
                "rice": rice,
                "revenue": revenue,
                "roi": roi,
                "deal": raw.get("deal") or "none",
                "dealValue": deal_value,
                "churn": raw.get("churn") or "none",
                "churnArr": _num(raw.get("churnArr")),
                "debtAdded": raw.get("debtAdded") or "none",
                "debtReduced": raw.get("debtReduced") or "none",
                "blocksOthers": bool(raw.get("blocksOthers")),
                "compliance": bool(raw.get("compliance")),
                "timeSensitive": bool(raw.get("timeSensitive")),
                "blockedBy": bool(raw.get("blockedBy")),
                "revEff": revenue / effort,
                "debt": debt,
                "urgency": max(urgency, 0),
                "loadPct": min(max(_num(raw.get("loadPct"), 20), 0.1), 100),
            }
        )

    if not scored:
        raise RuntimeError("Add backlog items to rank.")

    capacity = min(max(_num(payload.get("capacity"), 50), 0), 100)
    room = 100 - capacity

    rice_n = _norm([s["rice"] for s in scored])
    rev_n = _norm([s["revEff"] for s in scored])
    roi_n = _norm([s["roi"] for s in scored])
    deal_n = _norm([s["dealValue"] for s in scored])
    churn_n = _norm([s["churnArr"] * LEVELS.get(s["churn"], 0) for s in scored])
    debt_n = [(s["debt"] + 1) / 2 for s in scored]
    urg_n = _norm([s["urgency"] for s in scored])

    ranked = []
    for i, item in enumerate(scored):
        parts = [
            ("RICE", 0.20, rice_n[i]),
            ("Revenue / effort", 0.16, rev_n[i]),
            ("ROI", 0.08, roi_n[i]),
            ("Go / no-go", 0.18, deal_n[i]),
            ("Churn if skipped", 0.18, churn_n[i]),
            ("Debt", 0.08, debt_n[i]),
            ("Urgency", 0.12, urg_n[i]),
        ]
        composite = 100 * sum(weight * value for _, weight, value in parts)
        drivers = sorted(parts, key=lambda p: p[2] * p[1], reverse=True)
        ranked.append(
            {
                **{k: v for k, v in item.items() if k not in {"revEff", "debt", "urgency"}},
                "score": round(composite, 1),
                "rice": round(item["rice"], 1),
                "why": _reason_bits(item, item["rice"], drivers),
                "drivers": [{"name": n, "weight": w, "value": round(v, 2)} for n, w, v in drivers],
            }
        )

    ranked.sort(key=lambda x: (-x.get("mustRank", 0), -x["score"], x["effort"]))
    remaining = list(ranked)
    waves = []
    while remaining:
        anchor = None
        for item in remaining:
            if item["must"] or item["loadPct"] <= room + 1e-6:
                anchor = item
                break
        if anchor is None:
            break
        slack = room - anchor["loadPct"]
        wave = [anchor]
        rest = [item for item in remaining if item["id"] != anchor["id"]]
        fillers = [
            item
            for item in rest
            if item["loadPct"] <= slack + 1e-6 and item["effort"] <= anchor["effort"] + 1e-6
        ]
        fillers.sort(key=lambda item: (item["effort"], item["loadPct"], item["score"]))
        for item in fillers:
            if item["loadPct"] <= slack + 1e-6:
                wave.append(item)
                slack -= item["loadPct"]
        waves.append(wave)
        taken = {item["id"] for item in wave}
        remaining = [item for item in remaining if item["id"] not in taken]

    now, later = [], []
    step = 0
    for index, wave in enumerate(waves):
        titles = [item["title"] for item in wave]
        ids = [item["id"] for item in wave]
        load = round(sum(item["loadPct"] for item in wave), 1)
        duration = max(item["effort"] for item in wave)
        when = "this period" if index == 0 else "later"
        anchor = wave[0]
        for offset, item in enumerate(wave):
            step += 1
            others = [title for title in titles if title != item["title"]]
            item["when"] = when
            item["wave"] = index + 1
            item["waveLoad"] = load
            item["waveDuration"] = duration
            item["parallelIds"] = [item_id for item_id in ids if item_id != item["id"]]
            item["parallelTitles"] = others
            item["step"] = step
            item["parallelWith"] = None if offset == 0 else anchor["title"]
            item["rationale"] = _order_why(
                item,
                "main" if offset == 0 else "side",
                room,
                index + 1,
                anchor,
            )
            (now if index == 0 else later).append(item)
    for item in remaining:
        item["when"] = "later"
        item["wave"] = None
        item["waveLoad"] = item["loadPct"]
        item["waveDuration"] = item["effort"]
        item["parallelIds"] = []
        item["parallelTitles"] = []
        item["step"] = None
        item["parallelWith"] = None
        item["rationale"] = _order_why(item, "blocked", room, 0)
        later.append(item)
    ranked = now + later
    must_days = round(sum(i["effort"] for i in ranked if i["must"] and i["when"] == "this period"), 2)

    deal_now = sum(i["dealValue"] for i in now)
    churn_protected = sum(i["churnArr"] * LEVELS.get(i["churn"], 0) for i in now)
    return {
        "kind": "priority",
        "summary": (
            f"You're at {capacity:g}% capacity ({room:g}% free). Do this in order."
            if now
            else f"You're at {capacity:g}% capacity ({room:g}% free). Nothing fits in parallel yet."
        ),
        "capacity": capacity,
        "room": round(room, 1),
        "waves": len(waves),
        "mustDays": must_days,
        "dealValueNow": deal_now,
        "churnProtected": round(churn_protected, 0),
        "items": ranked,
        "nowIds": [i["id"] for i in now],
        "laterIds": [i["id"] for i in later],
        "generatedAt": datetime.now(timezone.utc).isoformat(),
    }
