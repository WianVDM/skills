#!/usr/bin/env python3
"""Shared frontmatter parser for debrief scripts.

Reads JSON from stdin with the contract described in the debrief skill design
and writes JSON to stdout. Also exposes backward-compatible helpers:

    parse_frontmatter(text: str) -> dict
    dump_frontmatter(data: dict, text: str = "") -> str

Usage:
    echo '{"source":"/path/to/file.md","source_type":"file","strict":false}' | python _frontmatter.py
"""

import json
import re
import sys
from datetime import date, datetime, timezone
from pathlib import Path


def _parse_scalar(value: str):
    """Parse a simple YAML scalar value."""
    value = value.strip()
    if not value or value in ("null", "Null", "NULL", "None", "none", "~"):
        return None
    low = value.lower()
    if low in ("true", "yes"):
        return True
    if low in ("false", "no"):
        return False
    if low in ("null", "none", "~"):
        return None
    # Quoted string
    if len(value) >= 2 and (
        (value.startswith('"') and value.endswith('"'))
        or (value.startswith("'") and value.endswith("'"))
    ):
        return value[1:-1]
    try:
        return int(value)
    except ValueError:
        pass
    try:
        return float(value)
    except ValueError:
        pass
    return value


def _fallback_parse(fm_text: str) -> dict:
    """Parse a simple YAML-like frontmatter block.

    Supports:
      - key: value
      - key:
          - item1
          - item2
      - key:
          nested_key: value
      - list-of-dicts under a key

    Does not support multi-line scalars, anchors, aliases, or complex types.
    """
    data = {}
    current_key = None
    current_list = None
    current_dict = None

    def _flush():
        if current_key is None:
            return
        if current_list:
            data[current_key] = current_list
        elif current_dict:
            data[current_key] = current_dict
        else:
            data[current_key] = None

    for raw_line in fm_text.splitlines():
        line = raw_line.rstrip()
        if not line:
            continue
        stripped = line.lstrip()
        if stripped.startswith("#"):
            continue
        indent = len(line) - len(stripped)

        # Top-level key
        if indent == 0 and ":" in stripped:
            _flush()
            key, sep, value = stripped.partition(":")
            key = key.strip()
            value = value.strip()
            if not value:
                current_key = key
                current_list = []
                current_dict = {}
            else:
                data[key] = _parse_scalar(value)
                current_key = None
                current_list = None
                current_dict = None
            continue

        # Nested content under a top-level key
        if current_key is not None and indent > 0:
            if stripped.startswith("- "):
                item = stripped[2:].strip()
                if ":" in item:
                    k, sep, v = item.partition(":")
                    k = k.strip()
                    v = v.strip()
                    current_list.append({k: _parse_scalar(v)})
                else:
                    current_list.append(_parse_scalar(item))
            elif ":" in stripped:
                k, sep, v = stripped.partition(":")
                k = k.strip()
                v = v.strip()
                current_dict[k] = _parse_scalar(v)
            # else: ignore unknown continuation lines
            continue

    _flush()
    return data


def _normalize(value):
    """Recursively convert datetime/date objects to ISO strings."""
    if isinstance(value, dict):
        return {k: _normalize(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_normalize(v) for v in value]
    if isinstance(value, datetime):
        if value.tzinfo is not None:
            return value.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        return value.strftime("%Y-%m-%dT%H:%M:%S")
    if isinstance(value, date):
        return value.isoformat()
    return value


def parse_frontmatter(text: str, strict: bool = False) -> dict:
    """Parse the YAML frontmatter block at the start of `text`.

    Returns an empty dict if no frontmatter is found. Raises ValueError if
    the frontmatter is malformed and cannot be parsed.
    """
    if not text or not text.startswith("---"):
        return {}

    end = text.find("---", 3)
    if end == -1:
        raise ValueError("frontmatter start marker '---' found but no closing marker")

    fm_text = text[3:end].strip()
    if not fm_text:
        return {}

    if strict:
        import yaml

        return _normalize(yaml.safe_load(fm_text)) or {}

    try:
        import yaml

        return _normalize(yaml.safe_load(fm_text)) or {}
    except ImportError:
        return _fallback_parse(fm_text)
    except Exception as exc:
        try:
            return _fallback_parse(fm_text)
        except Exception as fallback_exc:
            raise ValueError(
                f"failed to parse frontmatter: {exc}; fallback also failed: {fallback_exc}"
            ) from exc


def _serialize_value(value, indent: int = 0) -> str:
    """Serialize a simple value for the fallback dumper."""
    prefix = "  " * indent
    if isinstance(value, dict):
        lines = []
        for k, v in value.items():
            if isinstance(v, (dict, list)):
                lines.append(f"{prefix}{k}:")
                lines.append(_serialize_value(v, indent + 1))
            else:
                lines.append(f"{prefix}{k}: {_serialize_scalar(v)}")
        return "\n".join(lines)
    if isinstance(value, list):
        lines = []
        for item in value:
            if isinstance(item, dict):
                # list-of-dicts: first line uses '- key: value', rest indented
                first = True
                for k, v in item.items():
                    if first:
                        lines.append(f"{prefix}- {k}: {_serialize_scalar(v)}")
                        first = False
                    else:
                        lines.append(f"{prefix}  {k}: {_serialize_scalar(v)}")
            else:
                lines.append(f"{prefix}- {_serialize_scalar(item)}")
        return "\n".join(lines)
    return f"{prefix}{_serialize_scalar(value)}"


def _serialize_scalar(value) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    escaped = str(value).replace('"', '\\"')
    return f'"{escaped}"'


def dump_frontmatter(data: dict, text: str = "") -> str:
    """Replace the frontmatter in `text` with `data`, or return new frontmatter.

    Uses PyYAML if available; otherwise a simple key-value serializer.
    """
    body = ""
    if text.startswith("---"):
        end = text.find("---", 3)
        if end != -1:
            body = text[end + 3 :].lstrip()

    try:
        import yaml

        fm = yaml.safe_dump(data, sort_keys=False, allow_unicode=True).strip()
    except ImportError:
        lines = []
        for key, value in data.items():
            if isinstance(value, (dict, list)):
                lines.append(f"{key}:")
                lines.append(_serialize_value(value, 1))
            else:
                lines.append(f"{key}: {_serialize_scalar(value)}")
        fm = "\n".join(lines)

    if body:
        return f"---\n{fm}\n---\n\n{body}"
    return f"---\n{fm}\n---\n"


def _read_source(source: str, source_type: str) -> str:
    if source_type == "file":
        return Path(source).read_text(encoding="utf-8", errors="ignore")
    if source_type == "string":
        return source
    raise ValueError(f"invalid source_type: {source_type!r}; expected 'file' or 'string'")


def _run_from_json(data: dict) -> dict:
    source = data.get("source")
    source_type = data.get("source_type")
    strict = bool(data.get("strict", False))

    if not source or not source_type:
        return {
            "status": "error",
            "frontmatter": {},
            "body": "",
            "errors": ["source and source_type are required"],
        }

    try:
        text = _read_source(source, source_type)
    except Exception as exc:
        return {
            "status": "error",
            "frontmatter": {},
            "body": "",
            "errors": [f"failed to read source: {exc}"],
        }

    if not text.startswith("---"):
        return {
            "status": "missing",
            "frontmatter": {},
            "body": text,
            "errors": [],
        }

    try:
        fm = parse_frontmatter(text, strict=strict)
    except Exception as exc:
        return {
            "status": "error",
            "frontmatter": {},
            "body": text,
            "errors": [str(exc)],
        }

    end = text.find("---", 3)
    body = text[end + 3 :].lstrip("\n") if end != -1 else text

    return {
        "status": "parsed",
        "frontmatter": fm,
        "body": body,
        "errors": [],
    }


def _help() -> str:
    return """_frontmatter.py — parse YAML frontmatter from markdown

Reads JSON from stdin:
  {"source": "<path or string>", "source_type": "file" | "string", "strict": false}

Writes JSON to stdout:
  {"status": "parsed" | "missing" | "error", "frontmatter": {...}, "body": "...", "errors": []}
"""


if __name__ == "__main__":
    if any(arg in ("-h", "--help") for arg in sys.argv[1:]):
        print(_help())
        sys.exit(0)

    try:
        data = json.load(sys.stdin)
    except Exception as exc:
        print(
            json.dumps(
                {
                    "status": "error",
                    "frontmatter": {},
                    "body": "",
                    "errors": [f"invalid JSON input: {exc}"],
                }
            ),
            file=sys.stderr,
        )
        sys.exit(2)

    result = _run_from_json(data)
    print(json.dumps(result, indent=2))
    sys.exit(0 if result["status"] != "error" else 1)
