#!/usr/bin/env python3
"""research-ticket.py — deterministic ticket research helper.

Reads a JSON request from stdin, fetches ticket data from the configured tracker,
and writes a normalized JSON response to stdout.

Usage:
    python3 research-ticket.py < request.json
    python3 research-ticket.py --help
"""

import json
import os
import re
import sys
from base64 import b64encode
from urllib.error import HTTPError
from urllib.request import Request, urlopen

DEFAULT_SCOPE = [
    "core",
    "comments",
    "attachments",
    "history",
    "dev_info",
    "related",
    "worklog",
]

HELP = """research-ticket.py — fetch and normalize ticket data.

Usage:
    python3 research-ticket.py < request.json
    python3 research-ticket.py --help

Input JSON fields:
  ticket_key      (string, required) Ticket or issue key.
  project         (string, optional) Project key for validation.
  tracker         (string, required) One of: jira, github, linear, manual.
  tracker_config  (object, required) Tracker-specific config.
  scope           (string[], optional) Categories to fetch.
  manual_context  (object, optional) Required when tracker is manual.

Output JSON:
  status          complete | partial | needs_input | blocked
  ticket          Normalized core ticket fields.
  comments        List of comments.
  attachments     List of attachment metadata.
  history         List of status transitions.
  dev_info        Linked PRs, branches, commits.
  related_tickets Parent, children, duplicates, linked, blocked_by, blocks.
  worklog         Time tracking entries.
  context_graph   Sources that contributed to the result.
"""


def main():
    if len(sys.argv) > 1 and sys.argv[1] in ("-h", "--help"):
        print(HELP)
        sys.exit(0)

    try:
        data = json.load(sys.stdin)
    except Exception as exc:  # noqa: BLE001
        print(json.dumps({"status": "error", "errors": [f"Invalid JSON input: {exc}"]}, indent=2))
        sys.exit(2)

    if not isinstance(data, dict):
        print(json.dumps({"status": "error", "errors": ["Input must be a JSON object."]}, indent=2))
        sys.exit(2)

    try:
        result = dispatch(data)
    except Exception as exc:  # noqa: BLE001
        print(json.dumps({"status": "error", "errors": [f"Runtime failure: {exc}"]}, indent=2))
        sys.exit(1)
    print(json.dumps(result, indent=2))


def dispatch(data):
    ticket_key = data.get("ticket_key")
    tracker = data.get("tracker")
    tracker_config = data.get("tracker_config") or {}
    scope = data.get("scope") or list(DEFAULT_SCOPE)
    manual_context = data.get("manual_context") or {}

    if not ticket_key or not isinstance(ticket_key, str):
        return error_output("needs_input", "ticket_key is required and must be a string.")

    if tracker not in ("jira", "github", "linear", "manual"):
        return error_output(
            "needs_input",
            f"tracker must be one of jira, github, linear, manual; got {tracker!r}",
        )

    if tracker == "manual":
        return manual_adapter(ticket_key, scope, manual_context)

    missing = validate_tracker_config(tracker, tracker_config)
    if missing:
        return error_output(
            "needs_input",
            "Missing required tracker configuration or environment variables.",
            missing_env_vars=missing,
        )

    if tracker == "jira":
        return jira_adapter(ticket_key, tracker_config, scope)
    if tracker == "github":
        return github_adapter(ticket_key, tracker_config, scope)
    if tracker == "linear":
        return linear_adapter(ticket_key, tracker_config, scope)

    return error_output("blocked", f"Unhandled tracker: {tracker}")


def validate_tracker_config(tracker, cfg):
    """Return a list of missing environment variable / config names."""
    missing = []

    if not cfg.get("token_env"):
        missing.append("tracker_config.token_env")
    else:
        token_name = cfg.get("token_env")
        if token_name not in os.environ or not os.environ[token_name]:
            missing.append(token_name)

    if tracker == "jira":
        if not cfg.get("server_url"):
            missing.append("tracker_config.server_url")
        if cfg.get("username_env"):
            username_name = cfg.get("username_env")
            if username_name not in os.environ or not os.environ[username_name]:
                missing.append(username_name)

    if tracker == "github":
        if not cfg.get("repo"):
            missing.append("tracker_config.repo")

    return missing


def _extract_jira_dev_info(fields, scope):
    """Extract development (PR/branch/commit) info from Jira fields.

    If the development field is not present, return a gap note so the caller
    knows the data is unavailable rather than silently empty.
    """
    dev_info = {"prs": [], "branches": [], "commits": []}
    if "dev_info" not in scope:
        return dev_info, []

    development = fields.get("development")
    if isinstance(development, dict):
        prs = []
        for item in development.get("pullRequests", development.get("prs", [])):
            url = item.get("url") or item.get("displayId") or ""
            if url:
                prs.append(url)
        branches = [
            b.get("name", "") or b.get("displayId", "")
            for b in development.get("branches", [])
        ]
        commits = [
            c.get("id", "") or c.get("displayId", "")
            for c in development.get("commits", [])
        ]
        dev_info = {
            "prs": [p for p in prs if p],
            "branches": [b for b in branches if b],
            "commits": [c for c in commits if c],
        }
        return dev_info, []

    return dev_info, [
        "Jira development field is not available; linked PRs, branches, and commits could not be retrieved."
    ]


# ---------------------------------------------------------------------------
# Adapters
# ---------------------------------------------------------------------------

def manual_adapter(ticket_key, scope, context):
    if not context:
        return error_output(
            "needs_input",
            "manual_context is required when tracker is manual.",
        )

    ticket = {
        "key": ticket_key,
        "source": "manual",
        "summary": context.get("summary", ""),
        "description": context.get("description", ""),
        "issue_type": context.get("issue_type", ""),
        "status": context.get("status", ""),
        "priority": context.get("priority", ""),
        "assignee": context.get("assignee", ""),
        "reporter": context.get("reporter", ""),
        "created_at": context.get("created_at", ""),
        "updated_at": context.get("updated_at", ""),
        "labels": list(context.get("labels", [])),
        "components": list(context.get("components", [])),
        "acceptance_criteria": list(
            context.get("acceptance_criteria")
            or infer_acceptance_criteria(context.get("description", ""))
        ),
    }

    comments = list(context.get("comments", [])) if "comments" in scope else []
    attachments = list(context.get("attachments", [])) if "attachments" in scope else []
    history = list(context.get("history", [])) if "history" in scope else []
    dev_info = context.get("dev_info") if "dev_info" in scope else None
    related = context.get("related_tickets") if "related" in scope else None
    worklog = list(context.get("worklog", [])) if "worklog" in scope else []

    status = "complete" if (ticket["summary"] or ticket["description"]) else "partial"

    return build_output(
        status=status,
        ticket=ticket,
        comments=comments,
        attachments=attachments,
        history=history,
        dev_info=dev_info,
        related=related,
        worklog=worklog,
        context_graph=build_context_graph(ticket_key, scope, ["manual_context"]),
    )


def jira_adapter(ticket_key, cfg, scope):
    server_url = cfg["server_url"].rstrip("/")
    token_name = cfg["token_env"]
    credential = os.environ[token_name]
    username = None
    if cfg.get("username_env"):
        username = os.environ.get(cfg["username_env"])

    fields = [
        "summary",
        "description",
        "status",
        "priority",
        "assignee",
        "reporter",
        "labels",
        "components",
        "issuetype",
        "development",
        "issuelinks",
        "attachment",
        "comment",
        "worklog",
        "created",
        "updated",
        "parent",
        "subtasks",
    ]
    url = (
        f"{server_url}/rest/api/2/issue/{ticket_key}"
        f"?expand=changelog"
        f"&fields={','.join(fields)}"
    )
    req = Request(url, headers={"Accept": "application/json"})
    if username:
        creds = f"{username}:{credential}".encode("utf-8")
        req.add_header("Authorization", f"Basic {b64encode(creds).decode('ascii')}")
    else:
        req.add_header("Authorization", f"Bearer {credential}")

    try:
        with urlopen(req, timeout=15) as resp:
            body = json.loads(resp.read().decode("utf-8"))
    except HTTPError as exc:
        if exc.code == 404:
            return error_output(
                "blocked",
                f"Jira issue {ticket_key} not found on {server_url}.",
                http_status=exc.code,
            )
        return error_output(
            "needs_input",
            f"Jira API request failed: HTTP {exc.code} {exc.reason}.",
        )
    except Exception as exc:  # noqa: BLE001
        return error_output("needs_input", f"Jira API request failed: {exc}")

    return normalize_jira(body, scope, cfg)


def normalize_jira(issue, scope, cfg):
    fields = issue.get("fields", {})
    key = issue.get("key", "")

    description = extract_text(fields.get("description"))
    acceptance = infer_acceptance_criteria(description) if description else []
    # If explicit custom acceptance criteria field exists, prefer it (not in scope for v1).

    ticket = {
        "key": key,
        "source": "jira",
        "summary": extract_text(fields.get("summary")),
        "description": description,
        "issue_type": (fields.get("issuetype") or {}).get("name", ""),
        "status": (fields.get("status") or {}).get("name", ""),
        "priority": (fields.get("priority") or {}).get("name", ""),
        "assignee": ((fields.get("assignee") or {}).get("displayName", "")),
        "reporter": ((fields.get("reporter") or {}).get("displayName", "")),
        "created_at": fields.get("created", ""),
        "updated_at": fields.get("updated", ""),
        "labels": list(fields.get("labels", [])),
        "components": [c.get("name", "") for c in fields.get("components", [])],
        "acceptance_criteria": acceptance,
    }

    status = "complete"
    gaps = []

    comments = []
    if "comments" in scope:
        for c in fields.get("comment", {}).get("comments", []):
            comments.append({
                "author": (c.get("author") or {}).get("displayName", ""),
                "body": extract_text(c.get("body")),
                "created_at": c.get("created", ""),
            })

    attachments = []
    if "attachments" in scope:
        for a in fields.get("attachment", []):
            attachments.append({
                "filename": a.get("filename", ""),
                "content_type": a.get("mimeType", ""),
                "size": a.get("size", 0),
                "url": a.get("content", ""),
                "summary": f"Attachment: {a.get('filename', '')}",
            })

    history = []
    if "history" in scope:
        changelog = issue.get("changelog", {}).get("histories", [])
        for h in changelog:
            for item in h.get("items", []):
                if item.get("field") == "status":
                    history.append({
                        "from": item.get("fromString", ""),
                        "to": item.get("toString", ""),
                        "at": h.get("created", ""),
                        "author": (h.get("author") or {}).get("displayName", ""),
                    })

    related = {
        "parent": None,
        "children": [],
        "duplicates": [],
        "linked": [],
        "blocked_by": [],
        "blocks": [],
    }
    if "related" in scope:
        parent = fields.get("parent")
        if parent:
            related["parent"] = parent.get("key")
        for st in fields.get("subtasks", []):
            related["children"].append(st.get("key", ""))
        for link in fields.get("issuelinks", []):
            ltype = (link.get("type") or {}).get("name", "").lower()
            outward = link.get("outwardIssue")
            inward = link.get("inwardIssue")
            target = outward or inward
            if not target:
                continue
            tkey = target.get("key", "")
            if ltype in ("duplicate", "duplicates", "cloners", "cloned"):
                related["duplicates"].append(tkey)
            elif ltype in ("blocks", "block"):
                if outward:
                    related["blocks"].append(tkey)
                else:
                    related["blocked_by"].append(tkey)
            else:
                related["linked"].append(tkey)

    dev_info, dev_gaps = _extract_jira_dev_info(fields, scope)
    gaps.extend(dev_gaps)
    if dev_gaps:
        status = "partial"

    worklog = []
    if "worklog" in scope:
        for w in fields.get("worklog", {}).get("worklogs", []):
            worklog.append({
                "author": (w.get("author") or {}).get("displayName", ""),
                "time_spent": w.get("timeSpent", ""),
                "started": w.get("started", ""),
                "comment": extract_text(w.get("comment")),
            })

    context_sources = ["jira"]

    return build_output(
        status=status,
        ticket=ticket,
        comments=comments,
        attachments=attachments,
        history=history,
        dev_info=dev_info,
        related=related,
        worklog=worklog,
        context_graph=build_context_graph(key, scope, context_sources),
        gaps=gaps,
    )


def github_adapter(ticket_key, cfg, scope):
    credential = os.environ[cfg["token_env"]]
    repo = cfg["repo"]
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {credential}",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    number = parse_issue_number(ticket_key)
    if number:
        issue_url = f"https://api.github.com/repos/{repo}/issues/{number}"
    else:
        issue_url = (
            f"https://api.github.com/search/issues"
            f"?q={ticket_key}+repo:{repo}"
        )

    try:
        with urlopen(Request(issue_url, headers=headers), timeout=15) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
    except HTTPError as exc:
        if exc.code == 404:
            return error_output(
                "blocked",
                f"GitHub issue {ticket_key} not found in {repo}.",
                http_status=exc.code,
            )
        return error_output(
            "needs_input",
            f"GitHub API request failed: HTTP {exc.code} {exc.reason}.",
        )
    except Exception as exc:  # noqa: BLE001
        return error_output("needs_input", f"GitHub API request failed: {exc}")

    if number:
        issue = payload
    else:
        items = payload.get("items", [])
        if not items:
            return error_output(
                "blocked",
                f"GitHub issue {ticket_key} not found in {repo}.",
            )
        issue = items[0]

    comments = []
    gaps = []
    status = "complete"
    if "comments" in scope and issue.get("comments_url"):
        try:
            with urlopen(Request(issue["comments_url"], headers=headers), timeout=15) as resp:
                comments_raw = json.loads(resp.read().decode("utf-8"))
            comments = [
                {
                    "author": c.get("user", {}).get("login", ""),
                    "body": c.get("body", ""),
                    "created_at": c.get("created_at", ""),
                }
                for c in comments_raw
            ]
        except Exception as exc:  # noqa: BLE001
            gaps.append(f"GitHub comments could not be fetched: {exc}")
            status = "partial"

    return normalize_github(issue, comments, scope, cfg, status=status, gaps=gaps)


def normalize_github(issue, comments, scope, cfg, status="complete", gaps=None):
    if gaps is None:
        gaps = []

    description = issue.get("body", "") or ""
    ticket = {
        "key": str(issue.get("number", issue.get("id", ""))),
        "source": "github",
        "summary": issue.get("title", ""),
        "description": description,
        "status": issue.get("state", ""),
        "priority": "",
        "assignee": (issue.get("assignee") or {}).get("login", ""),
        "reporter": (issue.get("user") or {}).get("login", ""),
        "created_at": issue.get("created_at", ""),
        "updated_at": issue.get("updated_at", ""),
        "labels": [l.get("name", "") for l in issue.get("labels", [])],
        "components": [],
        "acceptance_criteria": infer_acceptance_criteria(description),
    }

    history = []
    if "history" in scope:
        # GitHub events can be fetched via /events; left as a known gap for v1.
        history = []

    dev_info = {"prs": [], "branches": [], "commits": []}
    if "dev_info" in scope:
        pr = issue.get("pull_request")
        if pr:
            dev_info["prs"].append(pr.get("html_url", ""))

    related = {
        "parent": None,
        "children": [],
        "duplicates": [],
        "linked": [],
        "blocked_by": [],
        "blocks": [],
    }
    if "related" in scope:
        # Extract issue/PR references from the body.
        for match in re.finditer(r"([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+#(\d+)|#(\d+))", description):
            ref = match.group(0)
            related["linked"].append(ref)
        related["linked"] = list(set(related["linked"]))

    attachments = []
    if "attachments" in scope:
        # GitHub issue attachments are embedded in the body as image links.
        for match in re.finditer(r"!\[([^\]]*)\]\(([^)]+)\)", description):
            attachments.append({
                "filename": match.group(1),
                "url": match.group(2),
                "summary": f"Inline image: {match.group(1)}",
            })

    worklog = []

    context_sources = ["github"]

    return build_output(
        status=status,
        ticket=ticket,
        comments=comments,
        attachments=attachments,
        history=history,
        dev_info=dev_info,
        related=related,
        worklog=worklog,
        context_graph=build_context_graph(ticket["key"], scope, context_sources),
        gaps=gaps,
    )


def linear_adapter(ticket_key, cfg, scope):
    credential = os.environ[cfg["token_env"]]
    team = cfg.get("team")
    headers = {
        "Content-Type": "application/json",
        "Authorization": credential,
    }

    # Linear issue identifiers are typically TEAM-123. Try to fetch by identifier.
    query = {
        "query": """
        query($identifier: String!) {
            issues(filter: { identifier: { eq: $identifier } }) {
                nodes {
                    id
                    identifier
                    title
                    description
                    state { name }
                    priority
                    createdAt
                    updatedAt
                    assignee { name }
                    creator { name }
                    team { name }
                    comments { nodes { id user { name } body createdAt } }
                    children { nodes { identifier } }
                    parent { identifier }
                    labels { nodes { name } }
                }
            }
        }
        """,
        "variables": {"identifier": ticket_key},
    }

    if team:
        # If team is provided, restrict to that team's issues.
        query = {
            "query": """
            query($identifier: String!, $teamKey: String!) {
                issues(filter: { identifier: { eq: $identifier }, team: { key: { eq: $teamKey } } }) {
                    nodes {
                        id
                        identifier
                        title
                        description
                        state { name }
                        priority
                        createdAt
                        updatedAt
                        assignee { name }
                        creator { name }
                        team { name }
                        comments { nodes { id user { name } body createdAt } }
                        children { nodes { identifier } }
                        parent { identifier }
                        labels { nodes { name } }
                    }
                }
            }
            """,
            "variables": {"identifier": ticket_key, "teamKey": team},
        }

    url = "https://api.linear.app/graphql"
    try:
        req = Request(
            url,
            data=json.dumps(query).encode("utf-8"),
            headers=headers,
            method="POST",
        )
        with urlopen(req, timeout=15) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
    except HTTPError as exc:
        if exc.code == 404:
            return error_output(
                "blocked",
                f"Linear issue {ticket_key} not found.",
                http_status=exc.code,
            )
        return error_output(
            "needs_input",
            f"Linear API request failed: HTTP {exc.code} {exc.reason}.",
        )
    except Exception as exc:  # noqa: BLE001
        return error_output("needs_input", f"Linear API request failed: {exc}")

    errors = payload.get("errors")
    if errors:
        return error_output(
            "needs_input",
            f"Linear API returned errors: {errors[0].get('message', errors)}",
        )

    nodes = payload.get("data", {}).get("issues", {}).get("nodes", [])
    if not nodes:
        return error_output(
            "blocked",
            f"Linear issue {ticket_key} not found.",
        )
    issue = nodes[0]
    return normalize_linear(issue, scope, cfg)


def normalize_linear(issue, scope, cfg):
    description = issue.get("description", "") or ""
    ticket = {
        "key": issue.get("identifier", ""),
        "source": "linear",
        "summary": issue.get("title", ""),
        "description": description,
        "status": (issue.get("state") or {}).get("name", ""),
        "priority": str(issue.get("priority", "")),
        "assignee": (issue.get("assignee") or {}).get("name", ""),
        "reporter": (issue.get("creator") or {}).get("name", ""),
        "created_at": issue.get("createdAt", ""),
        "updated_at": issue.get("updatedAt", ""),
        "labels": [l.get("name", "") for l in (issue.get("labels") or {}).get("nodes", [])],
        "components": [],
        "acceptance_criteria": infer_acceptance_criteria(description),
    }

    comments = []
    if "comments" in scope:
        for c in (issue.get("comments") or {}).get("nodes", []):
            comments.append({
                "author": (c.get("user") or {}).get("name", ""),
                "body": c.get("body", ""),
                "created_at": c.get("createdAt", ""),
            })

    related = {
        "parent": (issue.get("parent") or {}).get("identifier"),
        "children": [c.get("identifier", "") for c in (issue.get("children") or {}).get("nodes", [])],
        "duplicates": [],
        "linked": [],
        "blocked_by": [],
        "blocks": [],
    }

    context_sources = ["linear"]

    return build_output(
        status="complete",
        ticket=ticket,
        comments=comments,
        attachments=[],
        history=[],
        dev_info={"prs": [], "branches": [], "commits": []},
        related=related,
        worklog=[],
        context_graph=build_context_graph(ticket["key"], scope, context_sources),
    )


# ---------------------------------------------------------------------------
# Normalization helpers
# ---------------------------------------------------------------------------

def extract_text(value):
    """Extract plain text from a string or an Atlassian Document Format object."""
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        parts = []
        if value.get("type") == "doc" and "content" in value:
            for node in value.get("content", []):
                parts.append(_extract_adf_text(node))
            return "\n\n".join(p.strip() for p in parts if p.strip())
        return str(value)
    return str(value)


def _extract_adf_text(node):
    if not isinstance(node, dict):
        return str(node)
    if node.get("type") == "text":
        return node.get("text", "")
    if node.get("type") == "hardBreak":
        return "\n"
    text_parts = []
    for child in node.get("content", []):
        text_parts.append(_extract_adf_text(child))
    return "".join(text_parts)


def _ac_section_start(line):
    """Return True when a line opens an acceptance-criteria section.

    Accepts a markdown heading form (``## Acceptance Criteria`` or ``## AC``)
    and a label form with a trailing colon or dash (``Acceptance Criteria:``).
    """
    if re.match(r"^#{1,6}\s*(acceptance criteria|ac)\s*:?\s*$", line, re.IGNORECASE):
        return True
    return bool(re.match(r"^\s*(acceptance criteria|ac)\s*[:\-]", line, re.IGNORECASE))


def infer_acceptance_criteria(description):
    """Lightweight extraction of acceptance criteria from a description."""
    if not description:
        return []
    lines = description.splitlines()
    criteria = []
    in_section = False
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if _ac_section_start(stripped):
            in_section = True
            continue
        if in_section:
            if re.match(r"^#{1,6}\s", stripped):
                break
            # Strip leading bullet / checkbox markers.
            text = re.sub(r"^\s*[-*]\s+(\[[ x]\]\s*)?", "", stripped)
            text = re.sub(r"^\s*\d+\.\s+(\[[ x]\]\s*)?", "", text)
            if text:
                criteria.append(text)
    return criteria


def parse_issue_number(key):
    """Return a numeric issue number if the key looks like one, otherwise None."""
    if key.isdigit():
        return int(key)
    match = re.search(r"-(\d+)$", key)
    if match:
        return int(match.group(1))
    return None


def build_context_graph(key, scope, sources):
    graph = []
    if "core" in scope:
        graph.append({
            "source": "Core ticket",
            "key": key,
            "relevance": "High",
            "contribution": "Ticket summary, status, and fields",
        })
    if "comments" in scope:
        graph.append({
            "source": "Comments",
            "key": key,
            "relevance": "Medium",
            "contribution": "Chronological discussion",
        })
    if "attachments" in scope:
        graph.append({
            "source": "Attachments",
            "key": key,
            "relevance": "Medium",
            "contribution": "Evidence and supporting files",
        })
    if "history" in scope:
        graph.append({
            "source": "History",
            "key": key,
            "relevance": "Medium",
            "contribution": "Status transitions",
        })
    if "dev_info" in scope:
        graph.append({
            "source": "Development info",
            "key": key,
            "relevance": "High",
            "contribution": "Linked PRs, branches, commits",
        })
    if "related" in scope:
        graph.append({
            "source": "Related tickets",
            "key": key,
            "relevance": "High",
            "contribution": "Parent, children, links, duplicates",
        })
    if "worklog" in scope:
        graph.append({
            "source": "Worklog",
            "key": key,
            "relevance": "Low",
            "contribution": "Time spent on ticket",
        })
    for src in sources:
        graph.append({
            "source": src,
            "key": key,
            "relevance": "High",
            "contribution": "Tracker adapter source",
        })
    return graph


def build_output(
    status,
    ticket,
    comments=None,
    attachments=None,
    history=None,
    dev_info=None,
    related=None,
    worklog=None,
    context_graph=None,
    gaps=None,
):
    if dev_info is None:
        dev_info = {"prs": [], "branches": [], "commits": []}
    if related is None:
        related = {
            "parent": None,
            "children": [],
            "duplicates": [],
            "linked": [],
            "blocked_by": [],
            "blocks": [],
        }
    return {
        "status": status,
        "ticket": ticket,
        "comments": comments or [],
        "attachments": attachments or [],
        "history": history or [],
        "dev_info": dev_info,
        "related_tickets": related,
        "worklog": worklog or [],
        "context_graph": context_graph or [],
        "gaps": gaps or [],
    }


def error_output(status, message, missing_env_vars=None, http_status=None):
    out = build_output(status, {"key": "", "source": "", "summary": ""})
    out["message"] = message
    if missing_env_vars:
        out["missing_env_vars"] = missing_env_vars
    if http_status:
        out["http_status"] = http_status
    return out


if __name__ == "__main__":
    main()
