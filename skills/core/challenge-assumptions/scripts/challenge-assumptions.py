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
DEFAULT_PROXIMITY = 3

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


# Common verbs that can be negated with an auxiliary.
COPULA_VERBS = {"is", "are", "was", "were", "does", "did", "will", "would", "should", "can", "could"}


def normalize(text: str) -> str:
    """Lowercase and remove non-alphanumeric spacing for matching."""
    return re.sub(r"[^a-z0-9\s]", " ", text.lower())


def extract_words(text: str) -> list[str]:
    """Extract meaningful words from text."""
    return [w for w in normalize(text).split() if w and w not in STOP_WORDS]


def extract_key_phrases(text: str, max_phrases: int = DEFAULT_MAX_SIGNALS) -> list[str]:
    """Extract short noun/verb phrases from the assumption text, shortest first.

    Shorter phrases (e.g., "token refresh", "auth guard") produce more useful
    natural-language negations and synonyms than the full sentence.
    """
    words = extract_words(text)
    if len(words) < 2:
        return []
    phrases = []
    seen = set()
    # Build phrases from shortest to longest, excluding the full sentence.
    for length in range(2, min(len(words), 6) + 1):
        if length == len(words):
            continue
        for start in range(0, len(words) - length + 1):
            phrase = " ".join(words[start:start + length])
            if phrase not in seen:
                seen.add(phrase)
                phrases.append(phrase)
    return phrases[:max_phrases]


def _negation_variants(phrase: str) -> list[str]:
    """Return natural-language negations of a phrase."""
    signals = [
        f"not {phrase}",
        f"no {phrase}",
        f"never {phrase}",
        f"{phrase} is not",
        f"is not {phrase}",
        f"{phrase} are not",
        f"are not {phrase}",
        f"{phrase} was not",
        f"was not {phrase}",
        f"{phrase} does not",
        f"does not {phrase}",
        f"{phrase} did not",
        f"did not {phrase}",
        f"{phrase} not",
        f"missing {phrase}",
        f"removed {phrase}",
        f"replaced {phrase}",
        f"deprecated {phrase}",
        f"outdated {phrase}",
        f"obsolete {phrase}",
        f"superseded {phrase}",
        f"unsupported {phrase}",
        f"not supported {phrase}",
        f"not implemented {phrase}",
        f"not handled {phrase}",
        f"not applicable {phrase}",
        f"instead of {phrase}",
        f"rather than {phrase}",
    ]
    return signals



def generate_disproof_signals(assumption_text: str) -> list[str]:
    """Generate a list of natural-language disproof signals to search for."""
    words = extract_words(assumption_text)
    signals: list[str] = []
    seen: set[str] = set()

    def _add(signal: str) -> None:
        if signal and signal not in seen:
            signals.append(signal)
            seen.add(signal)

    # Phrase-level negations and synonyms are the primary signal source.
    for phrase in extract_key_phrases(assumption_text, max_phrases=DEFAULT_MAX_SIGNALS * 2):
        # Alternative handler phrasing first: "Y handles X" vs "X handled by Y".
        if len(phrase.split()) >= 2:
            _add(f"handles {phrase}")
            _add(f"{phrase} handled by")
            _add(f"handled by {phrase}")
        # Location-style negations.
        _add(f"not in {phrase}")
        _add(f"not at {phrase}")
        # Standard negations and synonyms.
        for signal in _negation_variants(phrase):
            _add(signal)

    # For very short assumptions, add a few simple whole-sentence negations.
    if len(words) <= 3:
        for signal in ("not " + " ".join(words), "no " + " ".join(words), "never " + " ".join(words)):
            _add(signal)

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


def _phrase_indices(source_words: list[str], phrase_words: list[str]) -> list[int]:
    """Return start indices of phrase in source_words, allowing 1-word gaps."""
    if not phrase_words:
        return []
    indices = []
    for i in range(len(source_words) - len(phrase_words) + 1):
        match = True
        for j, pw in enumerate(phrase_words):
            if i + j >= len(source_words) or source_words[i + j] != pw:
                match = False
                break
        if match:
            indices.append(i)
    return indices


def _marker_adjacent_to_phrase(source_words: list[str], phrase_words: list[str], marker: str, proximity: int) -> bool:
    """Return True if a contradiction marker appears within proximity words of phrase."""
    marker_words = marker.split()
    phrase_indices = _phrase_indices(source_words, phrase_words)
    if not phrase_indices:
        return False

    for idx in phrase_indices:
        # Check window [idx - proximity, idx + len(phrase) + proximity]
        start = max(0, idx - proximity)
        end = min(len(source_words), idx + len(phrase_words) + proximity)
        window = source_words[start:end]
        for i in range(len(window) - len(marker_words) + 1):
            if window[i:i + len(marker_words)] == marker_words:
                return True
    return False


def find_contradictions(assumption_text: str, signals: list[str], evidence: dict[str, str], context_window: int, proximity: int) -> list[dict[str, Any]]:
    """Search evidence for disproof signals adjacent to assumption phrases."""
    hits: list[dict[str, Any]] = []
    assumption_words = extract_words(assumption_text)
    if not assumption_words:
        return hits

    # Build phrase list: the full assumption and key phrases.
    key_phrases = extract_key_phrases(assumption_text, max_phrases=DEFAULT_MAX_SIGNALS)
    phrases = [" ".join(assumption_words)] + key_phrases

    for source_key, source_text in evidence.items():
        normalized_source = normalize(source_text)
        source_words = normalized_source.split()

        # Check adjacency of contradiction markers to assumption phrases.
        for phrase in phrases:
            phrase_words = phrase.split()
            if not phrase_words:
                continue
            for marker in CONTRADICTION_MARKERS:
                if _marker_adjacent_to_phrase(source_words, phrase_words, marker, proximity):
                    # Find an occurrence of the phrase in the source to build a snippet.
                    indices = _phrase_indices(source_words, phrase_words)
                    idx = indices[0] if indices else 0
                    start = max(0, idx - context_window)
                    end = min(len(source_words), idx + len(phrase_words) + context_window)
                    snippet = " ".join(source_words[start:end])
                    hit = {
                        "source": source_key,
                        "snippet": snippet,
                        "reason": f"contradiction marker '{marker}' adjacent to phrase '{phrase}'"
                    }
                    if hit not in hits:
                        hits.append(hit)
                    break

        # Also check for explicit disproof signals anywhere in the evidence.
        for signal in signals:
            if signal in normalized_source:
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
    proximity = int(input_data.get("proximity", DEFAULT_PROXIMITY))

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
        hits = find_contradictions(text, signals, flat_evidence, context_window, proximity)

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
