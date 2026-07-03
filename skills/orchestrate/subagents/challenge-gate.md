# Challenge Gate

## Purpose

Stress-test understanding before allowing the conductor to exit the loop and draft a plan.

## Inputs

- Current state.md.
- Config `preferred_challenge_skills`.
- Last skill run.

## Process

1. Select a challenge skill different from the last skill run.
2. Pass the current understanding and open questions to it.
3. Capture its challenge findings.
4. If any new gap, contradiction, or edge case is found:
   - Lower confidence.
   - Add gaps to open questions.
   - Recommend continuing the loop.
5. If no gaps are found, mark the challenge gate as passed.

## Outputs

- Challenge skill used.
- Summary of challenge findings.
- Whether the gate passed.
- Recommended next action.
