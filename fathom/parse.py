from __future__ import annotations

import json
import re
from typing import Any

SOURCE_ALIASES = {
    "interview": "interview",
    "transcripts": "interview",
    "transcript": "interview",
    "call": "sales",
    "sales": "sales",
    "gong": "sales",
    "support": "support",
    "ticket": "support",
    "zendesk": "support",
    "intercom": "support",
    "review": "review",
    "g2": "review",
    "appstore": "review",
    "slack": "slack",
    "cs": "slack",
    "customer success": "slack",
    "feature": "feature_request",
    "feature request": "feature_request",
    "canny": "feature_request",
    "productboard": "feature_request",
}

SEGMENT_ALIASES = {
    "enterprise": "enterprise",
    "ent": "enterprise",
    "mid-market": "mid-market",
    "midmarket": "mid-market",
    "mm": "mid-market",
    "startup": "startup",
    "smb": "startup",
    "unknown": "unknown",
}

HEADER_RE = re.compile(
    r"^(?:customer|account|company|source|type|segment|tier|date|when)\s*[:|-]\s*(.+)$",
    re.I,
)


def normalize_source(value: str | None) -> str:
    if not value:
        return "other"
    return SOURCE_ALIASES.get(value.strip().lower(), "other")


def normalize_segment(value: str | None) -> str:
    if not value:
        return "unknown"
    return SEGMENT_ALIASES.get(value.strip().lower(), "unknown")


def parse_prefixed_block(block: str) -> dict | None:
    lines = [ln.strip() for ln in block.split("\n") if ln.strip()]
    if not lines:
        return None
    customer = source = segment = date = None
    body: list[str] = []
    for line in lines:
        match = HEADER_RE.match(line)
        if not match:
            body.append(line)
            continue
        field = re.split(r"[:|-]", line, maxsplit=1)[0].strip().lower()
        value = match.group(1).strip()
        if field in {"customer", "account", "company"}:
            customer = value
        elif field in {"source", "type"}:
            source = value
        elif field in {"segment", "tier"}:
            segment = value
        elif field in {"date", "when"}:
            date = value
        else:
            body.append(line)
    text = " ".join(body).strip()
    if not text:
        return None
    return {"text": text, "customer": customer, "source": source, "segment": segment, "date": date}


def split_csv_line(line: str) -> list[str]:
    out: list[str] = []
    current = ""
    in_quotes = False
    i = 0
    while i < len(line):
        ch = line[i]
        if ch == '"':
            if in_quotes and i + 1 < len(line) and line[i + 1] == '"':
                current += '"'
                i += 1
            else:
                in_quotes = not in_quotes
        elif ch == "," and not in_quotes:
            out.append(current)
            current = ""
        else:
            current += ch
        i += 1
    out.append(current)
    return out


def parse_csv(text: str) -> list[dict]:
    lines = [ln for ln in text.splitlines() if ln.strip()]
    if len(lines) < 2:
        return []
    headers = [h.strip().lower() for h in split_csv_line(lines[0])]

    def idx(names: list[str]) -> int:
        for name in names:
            if name in headers:
                return headers.index(name)
        return -1

    text_idx = idx(["text", "feedback", "quote", "comment", "body", "message"])
    if text_idx == -1:
        return []
    customer_idx = idx(["customer", "account", "company", "org"])
    source_idx = idx(["source", "type", "channel"])
    segment_idx = idx(["segment", "tier", "plan"])
    date_idx = idx(["date", "created", "when"])
    rows = []
    for line in lines[1:]:
        cols = split_csv_line(line)
        if text_idx >= len(cols):
            continue
        body = cols[text_idx].strip()
        if not body:
            continue
        row: dict[str, Any] = {"text": body}
        if customer_idx >= 0 and customer_idx < len(cols):
            row["customer"] = cols[customer_idx]
        if source_idx >= 0 and source_idx < len(cols):
            row["source"] = cols[source_idx]
        if segment_idx >= 0 and segment_idx < len(cols):
            row["segment"] = cols[segment_idx]
        if date_idx >= 0 and date_idx < len(cols):
            row["date"] = cols[date_idx]
        rows.append(row)
    return rows


def looks_like_csv(text: str) -> bool:
    first = next((ln for ln in text.splitlines() if ln.strip()), "")
    headers = first.lower()
    return "," in headers and any(k in headers for k in ("text", "feedback", "quote"))


def parse_feedback_input(input_text: str) -> list[dict]:
    trimmed = input_text.strip()
    if not trimmed:
        return []
    if trimmed.startswith("[") or trimmed.startswith("{"):
        try:
            parsed = json.loads(trimmed)
            items = parsed if isinstance(parsed, list) else [parsed]
            out = []
            for item in items:
                if isinstance(item, str):
                    out.append({"text": item})
                elif isinstance(item, dict) and item.get("text"):
                    row = dict(item)
                    row["text"] = str(item["text"])
                    out.append(row)
            if out:
                return out
        except json.JSONDecodeError:
            pass
    if looks_like_csv(trimmed):
        csv = parse_csv(trimmed)
        if csv:
            return csv
    blocks = [b.strip() for b in re.split(r"\n\s*\n", trimmed) if b.strip()]
    from_blocks = [parse_prefixed_block(b) for b in blocks]
    from_blocks = [b for b in from_blocks if b]
    if len(from_blocks) >= 3:
        return from_blocks
    return [{"text": line.strip()} for line in trimmed.split("\n") if len(line.strip()) > 8]


def with_normalized_meta(raw: dict) -> dict:
    return {
        "text": str(raw.get("text", "")).strip(),
        "source": normalize_source(raw.get("source")),
        "customer": (str(raw["customer"]).strip() if raw.get("customer") else "Unknown customer"),
        "segment": normalize_segment(raw.get("segment")),
        "date": raw.get("date"),
        "id": raw.get("id"),
    }
