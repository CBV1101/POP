from __future__ import annotations

import base64
import json
import urllib.error
import urllib.parse
import urllib.request

USER_AGENT = "POP/0.1"


def _request(url: str, *, method: str = "GET", headers: dict | None = None, body: dict | None = None) -> dict:
    data = None if body is None else json.dumps(body).encode("utf-8")
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("User-Agent", USER_AGENT)
    req.add_header("Accept", "application/json")
    if body is not None:
        req.add_header("Content-Type", "application/json")
    for key, value in (headers or {}).items():
        req.add_header(key, value)
    try:
        with urllib.request.urlopen(req, timeout=25) as resp:
            raw = resp.read().decode("utf-8")
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as err:
        raise RuntimeError(f"{err.code} from {urllib.parse.urlparse(url).netloc}") from None
    except urllib.error.URLError as err:
        raise RuntimeError("Could not reach the backlog. Check the host and your network.") from None


def _as_items(rows: list[dict]) -> dict:
    return {"items": rows, "count": len(rows)}


def fetch_linear(token: str) -> dict:
    if not token:
        raise RuntimeError("Add a Linear personal API key.")
    auth = token if token.lower().startswith("bearer ") else f"Bearer {token}"
    payload = _request(
        "https://api.linear.app/graphql",
        method="POST",
        headers={"Authorization": auth},
        body={
            "query": """
            query PopBacklog {
              issues(
                first: 80
                filter: { state: { type: { nin: ["completed", "canceled"] } } }
              ) {
                nodes { identifier title description }
              }
            }
            """
        },
    )
    if payload.get("errors"):
        raise RuntimeError("Linear rejected the key. Check that it can read issues.")
    nodes = (((payload.get("data") or {}).get("issues") or {}).get("nodes")) or []
    items = []
    for node in nodes:
        title = (node.get("title") or "").strip()
        desc = (node.get("description") or "").strip()
        text = title if not desc else f"{title}. {desc.splitlines()[0]}"
        if not text:
            continue
        items.append(
            {
                "text": text[:500],
                "customer": node.get("identifier") or "Linear",
                "source": "feature_request",
                "segment": "unknown",
            }
        )
    if not items:
        raise RuntimeError("No open Linear issues found.")
    return _as_items(items)


def fetch_github(token: str, repo: str) -> dict:
    if not token:
        raise RuntimeError("Add a GitHub token with issue read access.")
    repo = (repo or "").strip().strip("/")
    if repo.count("/") != 1:
        raise RuntimeError("GitHub repo should look like owner/name.")
    payload = _request(
        f"https://api.github.com/repos/{repo}/issues?state=open&per_page=80",
        headers={"Authorization": f"Bearer {token}"},
    )
    if isinstance(payload, dict) and payload.get("message"):
        raise RuntimeError("GitHub rejected the request. Check the token and repo.")
    items = []
    for node in payload if isinstance(payload, list) else []:
        if node.get("pull_request"):
            continue
        title = (node.get("title") or "").strip()
        if not title:
            continue
        items.append(
            {
                "text": title,
                "customer": f"{repo}#{node.get('number')}",
                "source": "feature_request",
                "segment": "unknown",
            }
        )
    if not items:
        raise RuntimeError("No open GitHub issues found.")
    return _as_items(items)


def fetch_jira(host: str, email: str, token: str, jql: str) -> dict:
    host = (host or "").strip().replace("https://", "").replace("http://", "").rstrip("/")
    if not host or not email or not token:
        raise RuntimeError("Jira needs your site, email, and API token.")
    query = jql.strip() if jql and jql.strip() else "statusCategory != Done ORDER BY updated DESC"
    auth = base64.b64encode(f"{email}:{token}".encode("utf-8")).decode("ascii")
    params = urllib.parse.urlencode(
        {"jql": query, "maxResults": 80, "fields": "summary,description"}
    )
    payload = _request(
        f"https://{host}/rest/api/3/search?{params}",
        headers={"Authorization": f"Basic {auth}"},
    )
    issues = payload.get("issues") or []
    items = []
    for issue in issues:
        fields = issue.get("fields") or {}
        title = (fields.get("summary") or "").strip()
        if not title:
            continue
        items.append(
            {
                "text": title,
                "customer": issue.get("key") or "Jira",
                "source": "feature_request",
                "segment": "unknown",
            }
        )
    if not items:
        raise RuntimeError("No matching Jira issues found.")
    return _as_items(items)


def import_backlog(body: dict) -> dict:
    provider = (body.get("provider") or "").strip().lower()
    token = (body.get("token") or "").strip()
    if provider == "linear":
        return fetch_linear(token)
    if provider == "github":
        return fetch_github(token, body.get("repo") or "")
    if provider == "jira":
        return fetch_jira(body.get("host") or "", body.get("email") or "", token, body.get("jql") or "")
    raise RuntimeError("Choose Linear, GitHub, or Jira.")
