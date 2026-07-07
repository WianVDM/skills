#!/usr/bin/env python3
"""Robust frontmatter parser for debrief scripts.

Tries to use PyYAML if available; otherwise falls back to a simple, safe
key-value parser that handles the basic frontmatter produced by debrief
skills.

The parser is intentionally limited to the frontmatter conventions used by
the skill: YAML key-value pairs, lists, and one-level nested dicts. It does
not support arbitrary YAML features.

Usage:
    from _frontmatter import parse_frontmatter

    data = parse_frontmatter(text)
"""

import json
import re
from pathlib import Path


def _fallback_parse(fm_text: str) -> dict:
    """Parse a simple YAML-like frontmatter block.

    Supports:
      - key: value
      - key: "value"
      - key: 'value'
      - key:
          - item1
          - item2
      - key:
          nested_key: value

    Does not support multi-line scalars, anchors, aliases, or complex types.
    """
    data = {}
    current_key = None
    current_list = None
    current_dict = None

    for raw_line in fm_text.splitlines():
        line = raw_line.rstrip()
        if not line or line.startswith("#"):
            continue

        stripped = line.lstrip()
        indent = len(line) - len(stripped)

        # List item under a key
        if stripped.startswith("- ") and current_key is not None and indent > 0:
            item = stripped[2:].strip()
            # Check if the list item is a nested dict (e.g. "- assumption: test")
            if ":" in item:
                k, v = item.split(":", 1)
                k = k.strip()
                v = v.strip().strip('"').strip("'")
                if current_list is not None:
                    current_list.append({k: v})
                continue
            item = item.strip('"').strip("'")
            if current_list is not None:
                current_list.append(item)
            continue

        # Nested dict value
        if ":" in stripped and indent > 0 and current_key is not None and current_dict is not None:
            key, value = stripped.split(":", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            current_dict[key] = value
            continue

        # Top-level key
        if ":" in stripped and indent == 0:
            # Save previous collection if any
            if current_key is not None:
                if current_list is not None:
                    data[current_key] = current_list
                elif current_dict is not None:
                    data[current_key] = current_dict
                else:
                    data[current_key] = None

            key, value = stripped.split(":", 1)
            key = key.strip()
            value = value.strip()

            if not value:
                # Could be a list or dict on following lines
                current_key = key
                current_list = []
                current_dict = {}
                continue

            # Quoted value or plain scalar
            value = value.strip('"').strip("'")
            # Try common types
            if value.lower() in ("true", "yes"):
                value = True
            elif value.lower() in ("false", "no"):
                value = False
            elif value.lower() in ("null", "none", "~"):
                value = None
            elif value == "":
                value = None
            else:
                try:
                    value = int(value)
                except ValueError:
                    try:
                        value = float(value)
                    except ValueError:
                        pass
            data[key] = value
            current_key = None
            current_list = None
            current_dict = None
            continue

    # Flush any open collection
    if current_key is not None:
        if current_list is not None and current_list:
            data[current_key] = current_list
        elif current_dict is not None and current_dict:
            data[current_key] = current_dict
        else:
            data[current_key] = None

    return data


def parse_frontmatter(text: str) -> dict:
    """Parse the YAML frontmatter block at the start of `text`.

    Returns an empty dict if no frontmatter is found. Raises ValueError if
    the frontmatter is malformed and cannot be parsed.
    """
    if not text.startswith("---"):
        return {}

    end = text.find("---", 3)
    if end == -1:
        return {}

    fm_text = text[3:end].strip()
    if not fm_text:
        return {}

    try:
        import yaml
        return yaml.safe_load(fm_text) or {}
    except ImportError:
        return _fallback_parse(fm_text)
    except Exception as exc:
        # If PyYAML fails, try the fallback as a last resort.
        try:
            return _fallback_parse(fm_text)
        except Exception:
            raise ValueError(f"failed to parse frontmatter: {exc}") from exc


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
            if isinstance(value, list):
                lines.append(f"{key}:")
                for item in value:
                    lines.append(f"  - {item}")
            elif isinstance(value, dict):
                lines.append(f"{key}:")
                for k, v in value.items():
                    lines.append(f"  {k}: {v}")
            elif value is None:
                lines.append(f"{key}: null")
            elif isinstance(value, bool):
                lines.append(f"{key}: {'true' if value else 'false'}")
            elif isinstance(value, (int, float)):
                lines.append(f"{key}: {value}")
            else:
                escaped = str(value).replace('"', '\\"')
                lines.append(f'{key}: "{escaped}"')
        fm = "\n".join(lines)

    if body:
        return f"---\n{fm}\n---\n\n{body}"
    return f"---\n{fm}\n---\n"


if __name__ == "__main__":  # pragma: no cover - manual test
    sample = '''---
skill: debrief
version: 1.0.0
ticket: OC-4644
confidence: 85
baseline_complete: true
consumed_context:
  - {context_dir}/baseline/OC-4644.md
assumptions:
  - assumption: "test"
---

Body here.
'''
    print(json.dumps(parse_frontmatter(sample), indent=2))
