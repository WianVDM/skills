# Comment Triage

The goal of triage is to turn raw PR feedback into a concise, actionable issue board. Every comment and finding is challenged before it becomes an issue.

## Source types

Authors are classified via the `pr-report.bots` config map: match the comment or review author against each entry's `usernames`, then apply that entry's `source_type` and `default_severity`. Authors matching no entry whose name ends in `[bot]` (or is a known GitHub App) default to `automated_reviewer` at `recommended` severity with `low` confidence. All other unmapped authors are `human_reviewer`. This applies to every feedback surface: reviews, inline threads, and conversation comments.

| Source type | Description | Examples |
|-------------|-------------|----------|
| `static_analysis` | Automated code-quality enforcement | SonarQube, SonarCloud decorations |
| `automated_reviewer` | Bot that posts review-style comments | CodeRabbit |
| `hybrid_reviewer` | Automated tool running under a human account | Tate's T876 bot |
| `human_reviewer` | Human colleague | Any human reviewer |
| `ci_failure` | Failing check or build | GitHub Actions, Azure Pipelines |

## Severity levels

| Severity | Meaning | Must address? |
|----------|---------|---------------|
| `blocker` | CI/build failure or required check failing. Prevents merge. | Yes |
| `required` | Project code-quality rule violated. | Yes, or formally suppress |
| `required_to_resolve` | Human or hybrid reviewer comment. | Must reply/address |
| `recommended` | Suggestion that survived challenge. | Address if time |
| `informational` | FYI, style nit, or did not survive challenge. | No |

## Challenge rules

For every non-CI issue, ask:

1. **Relevance to PR changes:** Does this comment relate to code changed in this PR?
2. **Relevance to scope:** Does this comment relate to the ticket scope or PR intent?
3. **Duplication:** Is this the same concern as an already captured issue?
4. **Evidence:** Does the commenter provide evidence (line reference, failing test, rule violation)?
5. **Convention support:** Is there a project convention or rule that supports this comment?
6. **Actionability:** Is the comment actionable?

If relevance is missing → flag as `scope-drift` or `unrelated`, downgrade severity.
If duplicate → merge into existing issue.
If evidence or convention support is weak → mark as `opinion` / `informational`.

## Deduplication

Group comments that point to the same underlying issue:

- Same SonarQube rule key.
- Same CodeRabbit pattern.
- Same file + nearby line + similar meaning.
- Same underlying concern raised by multiple reviewers.

The report should say: *"3 comments point to the same unused-import issue."*

## Rebuttal detection

A rebuttal occurs when a reviewer replies to our "Resolved. ..." comment with a counter-question or disagreement.

- Mark the thread status as `open`.
- Flag as `REBUTTAL — requires response`.
- Increase severity to `required_to_resolve` if it was lower.

## Auto-resolution

Some tools auto-resolve comments when the diff changes (e.g., CodeRabbit, SonarQube).

- Classify as `auto` resolution.
- Still verify the underlying issue is actually fixed if severity was `required` or `blocker`.

## Dismissed comments

Comments we decide are not actionable are kept in state but marked `dismissed-with-reason` or `no-action-needed`. They do not appear in the chat summary but remain available for future iterations.
