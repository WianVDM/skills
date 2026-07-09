#!/usr/bin/env python3
"""
challenge-assumptions.py

Deterministic assumption-challenge script for the challenge-assumptions skill.
Reads JSON from stdin, generates disproof signals for each assumption, searches
the provided evidence for those signals, and returns structured challenge results.

This script does not call LLMs. It uses simple keyword/phrase matching and
contradiction-marker detection. It is intended to be invoked by the
challenge-assumptions skill in a conductor workflow.
"""
import argparse
import json
import re
import sys
from typing import Any

DEFAULT_MAX_SIGNALS = 10
DEFAULT_CONTEXT_WINDOW = 10

# Negation and contradiction markers used to detect disproof.
CONTRADICTION_MARKERS = {
    "not", "no", "never", "none", "nothing", "nobody", "nowhere",
    "isn't", "isnt", "arent", "aren't", "wasn't", "wasnt", "weren't", "werent",
    "doesn't", "doesnt", "didn't", "didnt", "don't", "dont", "won't", "wont",
    "can't", "cant", "cannot", "couldn't", "couldnt", "shouldn't", "shouldnt",
    "wouldn't", "wouldnt", "mustn't", "mustnt",
    "instead", "rather", "alternative", "missing", "removed", "deprecated",
    "outdated", "obsolete", "replaced", "superseded", "not supported", "unsupported",
    "not implemented", "not handled", "not applicable",
}

# Words that do not carry meaningful contradiction signal on their own.
STOP_WORDS = {
    "the", "and", "for", "with", "from", "this", "that", "when", "where",
    "how", "what", "does", "is", "are", "to", "in", "of", "a", "an", "or",
    "as", "it", "be", "by", "on", "at", "during", "will", "shall", "may",
    "might", "can", "could", "should", "would", "must", "has", "have", "had",
    "do", "did", "done", "been", "being", "am", "was", "were", "s", "t"
}


def normalize(text: str) -> str:
    """Lowercase and remove non-alphanumeric spacing for matching."""
    return re.sub(r"[^a-z0-9\s]", " ", text.lower())


def extract_words(text: str) -> list[str]:
    """Extract meaningful words from text."""
    return [w for w in normalize(text).split() if w and w not in STOP_WORDS]


def extract_key_phrases(text: str) -> list[str]:
    """Extract short noun/verb phrases from the assumption text."""
    words = extract_words(text)
    # Return progressively shorter tail phrases to catch different wordings.
    phrases = []
    for length in range(min(len(words), 6), 1, -1):
        for start in range(0, len(words) - length + 1):
            phrase = " ".join(words[start:start + length])
            if phrase not in phrases:
                phrases.append(phrase)
    # Limit to most informative longer phrases.
    return phrases[:DEFAULT_MAX_SIGNALS]


def generate_disproof_signals(assumption_text: str) -> list[str]:
    """Generate a list of disproof signals to search for."""
    words = extract_words(assumption_text)
    signals: list[str] = []
    seen = set()

    # Add negated versions of the whole assumption.
    for negation in ("not", "never", "no"):
        negated = f"{negation} {' '.join(words)}"
        if negated not in seen:
            signals.append(negated)
            seen.add(negated)

    # Add negation of common "is/are/does/was/will" patterns.
    for verb in ("is", "are", "was", "were", "does", "did", "will", "would", "should", "can", "could"):
        if words and words[0] == verb:
            negated = f"{verb} not {' '.join(words[1:])}".strip()
            if negated not in seen:
                signals.append(negated)
                seen.add(negated)
            negated_contraction = f"{verb}n't {' '.join(words[1:])}".strip()
            if negated_contraction not in seen:
                signals.append(negated_contraction)
                seen.add(negated_contraction)

    # Add key phrases with contradiction markers.
    for phrase in extract_key_phrases(assumption_text):
        for marker in CONTRADICTION_MARKERS:
            signal = f"{marker} {phrase}"
            if signal not in seen:
                signals.append(signal)
                seen.add(signal)

    # Add "instead of" / "rather than" variants for the core phrase.
    for phrase in extract_key_phrases(assumption_text)[:3]:
        for alt in ("instead of", "rather than"):
            signal = f"{alt} {phrase}"
            if signal not in seen:
                signals.append(signal)
                seen.add(signal)

    # Deduplicate while preserving order.
    return list(dict.fromkeys(signals))[:DEFAULT_MAX_SIGNALS]


def flatten_evidence(evidence: Any) -> dict[str, str]:
    """Flatten evidence values into a dict of key -> searchable string."""
    flat: dict[str, str] = {}
    if not isinstance(evidence, dict):
        return flat
    for key, value in evidence.items():
        if isinstance(value, str):
            flat[key] = value
        elif isinstance(value, (list, tuple)):
            flat[key] = "\n".join(str(v) for v in value)
        elif isinstance(value, dict):
            flat[key] = json.dumps(value, ensure_ascii=False)
        else:
            flat[key] = str(value)
    return flat


def find_contradictions(assumption_text: str, signals: list[str], evidence: dict[str, str], context_window: int) -> list[dict[str, Any]]:
    """Search evidence for disproof signals within a context window of the assumption text."""
    hits: list[dict[str, Any]] = []
    assumption_words = set(extract_words(assumption_text))
    if not assumption_words:
        return hits

    for source_key, source_text in evidence.items():
        normalized_source = normalize(source_text)
        source_words = normalized_source.split()

        # Find windows where assumption words appear close together.
        for i in range(len(source_words)):
            window = source_words[i:i + context_window]
            window_set = set(window)
            overlap = assumption_words & window_set
            if len(overlap) < min(2, len(assumption_words)):
                continue

            # Check if any contradiction marker appears in this window.
            for marker in CONTRADICTION_MARKERS:
                if marker in window:
                    snippet = " ".join(window)
                    hit = {
                        "source": source_key,
                        "snippet": snippet,
                        "reason": f"contradiction marker '{marker}' near assumption words"
                    }
                    if hit not in hits:
                        hits.append(hit)
                    break

        # Also check for explicit disproof signals anywhere in the evidence.
        for signal in signals:
            if signal in normalized_source:
                # Find the surrounding context for the snippet.
                idx = normalized_source.find(signal)
                start = max(0, idx - 40)
                end = min(len(normalized_source), idx + len(signal) + 40)
                snippet = normalized_source[start:end]
                hit = {
                    "source": source_key,
                    "snippet": snippet,
                    "reason": f"matched disproof signal '{signal}'"
                }
                if hit not in hits:
                    hits.append(hit)

    return hits


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="challenge-assumptions",
        description="Stress-test assumptions by searching evidence for disproof signals."
    )
    parser.add_argument(
        "--input-file",
        "-i",
        type=str,
        default=None,
        help="Path to a JSON file containing input. If omitted, reads JSON from stdin."
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.input_file:
        with open(args.input_file, "r", encoding="utf-8") as f:
            input_data = json.load(f)
    else:
        input_data = json.load(sys.stdin)

    if not isinstance(input_data, dict):
        print(json.dumps({"status": "blocked", "error": "Input must be a JSON object"}, indent=2))
        sys.exit(1)

    assumptions = input_data.get("assumptions") or []
    evidence = input_data.get("evidence") or {}
    max_signals = int(input_data.get("max_signals", DEFAULT_MAX_SIGNALS))
    context_window = int(input_data.get("context_window", DEFAULT_CONTEXT_WINDOW))

    if not isinstance(assumptions, list):
        print(json.dumps({"status": "needs_input", "error": "assumptions must be a list"}, indent=2))
        sys.exit(0)

    if not assumptions:
        print(json.dumps({"status": "needs_input", "error": "assumptions list is empty"}, indent=2))
        sys.exit(0)

    flat_evidence = flatten_evidence(evidence)
    results: list[dict[str, Any]] = []
    overall_status = "complete"

    for assumption in assumptions:
        if not isinstance(assumption, dict):
            results.append({
                "text": str(assumption),
                "status": "inconclusive",
                "notes": "Assumption is not a valid object.",
                "disproof_refs": []
            })
            overall_status = "partial"
            continue

        text = (assumption.get("text") or "").strip()
        basis = (assumption.get("basis") or "").strip()

        if not text:
            results.append({
                "text": "",
                "status": "inconclusive",
                "notes": "Assumption text is empty.",
                "disproof_refs": []
            })
            overall_status = "partial"
            continue

        signals = generate_disproof_signals(text)[:max_signals]
        hits = find_contradictions(text, signals, flat_evidence, context_window)

        if hits:
            disproof_refs = sorted({hit["source"] for hit in hits})
            evidence_found = [f"{hit['source']}: '{hit['snippet'][:200]}'" for hit in hits]
            notes = (
                f"Found {len(hits)} disproof signal(s) in {', '.join(disproof_refs)}. "
                "Caller decides whether confidence changes."
            )
            status = "challenged"
        else:
            disproof_refs = []
            evidence_found = []
            notes = (
                f"No disproof signals found for assumption."
                + (f" Basis: {basis}" if basis else "")
                + " Caller decides whether confidence changes."
            )
            status = "holds"

        results.append({
            "text": text,
            "status": status,
            "notes": notes,
            "disproof_refs": disproof_refs,
            "disproof_signals_searched": signals,
            "evidence_found": evidence_found
        })

    print(json.dumps({
        "status": overall_status,
        "assumptions": results
    }, indent=2))


if __name__ == "__main__":
    try:
        main()
    except json.JSONDecodeError as e:
        print(json.dumps({"status": "blocked", "error": f"Invalid JSON input: {e}"}, indent=2))
        sys.exit(1)
    except Exception as e:
        print(json.dumps({"status": "blocked", "error": f"Unexpected error: {e}"}, indent=2))
        sys.exit(1)
