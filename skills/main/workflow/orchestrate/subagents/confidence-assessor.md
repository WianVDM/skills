# Confidence Assessor

## Purpose

Update the confidence level and explanation after each loop iteration.

## Inputs

- Current state.md.
- Findings from the most recently run skill.
- Current open questions.

## Process

1. Review the updated understanding.
2. Review open questions and mark any as resolved.
3. Determine whether confidence should rise, fall, or stay the same.
4. Ensure confidence is not inflated.
5. Update the `## Confidence` section.

## Outputs

- New confidence level and percentage.
- One-sentence explanation.
- List of resolved open questions.
- List of new open questions.
