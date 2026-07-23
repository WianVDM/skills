# Review rubric

What a good review is, for `pr-review`. The synthesizer hunts by this rubric; the writer enforces it; the style profile (`pr-review.review.style` in config) adjusts it per project.

The rubric exists because reviews fail in two directions: too shallow (only bug-hunting, misses that reviews are mostly knowledge transfer and norm-keeping) and too noisy (nitpicks drowning the one comment that matters). Everything here fights one of those two failures.

## The governing rule

Approve when the change improves the codebase, even if it is not perfect. There is no perfect code, only better code. Blocking is reserved for things that move the codebase *backward* or break behavior. Everything else is a comment the author may act on or ignore, and it must be labeled so they can tell the difference without asking.

## Issue classes, in priority order

Hunt in this order. Blocking weight decreases down the list.

| # | Class | What to check | Default weight |
|---|---|---|---|
| 1 | Design | Does the change fit the system? Right home, right time, integrates with what exists? | Blocking when it moves the system in a wrong direction; otherwise a report discussion. |
| 2 | Functionality | Does it do what the author intended? Edge cases, error handling, concurrency, races. | Blocking when confirmed or high-confidence. |
| 3 | Complexity | Can a reader understand it quickly? Over-engineering: solving a speculated future problem instead of the one that exists. | Blocking when severe; `suggestion` otherwise. |
| 4 | Tests | Present for new logic, and *valid* — would this test actually fail if the code broke? A test that cannot fail is a defect, not coverage. | Missing tests: blocking when project convention requires them. Invalid tests: blocking. Brittle tests: suggestion. |
| 5 | Naming & comments | Names say what the thing is; comments explain *why*, not *what*. | Non-blocking unless genuinely misleading. |
| 6 | Style | Formatting, import order, preference-level patterns. | Never a review comment. Route to gates and linters. If the project has no gate for it and it matters, file it in the report as a chore for the user, not on the PR. |

Classes 1–4 are where reviews earn their keep. If a draft's comments cluster in classes 5–6, the review is noise regardless of how thorough it feels.

## Comment vocabulary

Every inline comment carries a label and, where needed, a decoration. The label makes intent explicit so the prose doesn't have to. Based on Conventional Comments, reduced to what a PR review actually uses.

Labels:

- `issue` — a problem with the change. Blocking unless decorated otherwise. Pair with a suggestion when you can.
- `suggestion` — a concrete improvement. Say what and why, briefly.
- `question` — you have a concern but are not sure it is real. Ask instead of asserting; the answer often settles it without a round of changes.
- `nitpick` — trivial preference. Always non-blocking. See the budget below before writing one.
- `praise` — something genuinely good. At most one per review; never manufactured.
- `note` — something the author should know, no action requested. Always non-blocking.
- `todo` — small, necessary task, usually process (update a doc, link a ticket).
- `chore` — process step before merge, with a pointer to how.

Decorations:

- `(blocking)` — must be resolved before merge. Default for `issue`; state it explicitly on anything else you intend to block on.
- `(non-blocking)` — merge may proceed regardless.
- `(if-minor)` — resolve only if the fix stays trivial.

Rendered form in the posted comment: `label (decorations): subject` then an optional short discussion. Config `review.style.render_labels` controls whether prefixes appear literally in posted text.

## Signal-to-noise budget

A review's value is its signal-to-noise ratio, not its thoroughness.

- Nitpicks never outnumber substantive comments.
- A nitpick survives only if it teaches the author something, prevents a future problem or a spreading pattern, or improves the user experience. Otherwise delete it.
- Anything a linter or formatter can catch goes to the targeted checks, not the review.
- More than ten inline comments usually means the PR needs a conversation, not a review. Say so in the user-facing report and propose the highest-weight items only.
- One real finding stated clearly beats five maybes. Low-confidence items go to the report, not the PR, unless framed as `question`.

## Phrasing rules

- Question-first unless the finding is a confirmed defect. "Is there a reason this bypasses the cache?" beats "this should use the cache." Questions surface context you lack; orders start fights.
- Cite behavior, not taste. Say what breaks, degrades, or misleads. "This is cleaner" is not a finding.
- One to three sentences per inline comment. If it needs more, the subject is wrong or it belongs in the top-level body.
- Human voice. No hedge phrases, no intensifiers, no "it is important to note." Write like a maintainer who has sixty seconds of the author's attention.
- Praise what is genuinely good, once. Never manufacture it; false praise is worse than none.

## Context and coverage rules

- **Read around the hunk.** For every changed file, read enough of the surrounding file to judge the change in context — callers, callees, invariants the file maintains. Most real findings live outside the diff. Findings from surrounding code anchor to the nearest changed line and name the target line in the text.
- **Review the tests as hard as the code.** Tests do not test themselves.
- **Review every changed line**, calibrating scrutiny — generated files and data blobs scan; hand-written logic gets read.
- **Size gate.** Past ~400 changed lines (`review.size_gate_lines` in config), review depth degrades no matter what. Disclose this in the user-facing report, suggest a split, and restrict the draft to design and functionality findings. Do not present a skim of a large PR as a thorough review.

## Event selection

- `REQUEST_CHANGES` — at least one blocking item.
- `APPROVE` — no blocking items. Optional comments may accompany it only when the style profile allows them for this reviewer position (see below).
- `COMMENT` — no blocking items but the user is not ready to approve, or findings are ambiguous.

Approve-optimistically is the default posture: when items are minor, approve and trust the author, rather than forcing another round-trip. The posture flips when config says so (`review.style.approve_optimistically: false`) — for junior authors, missing CI, or auto-merge setups.

## Reviewer position

The synthesizer determines the user's position from existing reviews before drafting:

- **First reviewer** — optional and "worth noting" comments are allowed, subject to the budget.
- **After an existing approval** — the second approver may merge. The review is clean: no optional comments, no nitpicks, no "worth noting." Blocking items still block. Config: `review.style.optional_comments.after_existing_approval: suppress`.

Config can loosen or tighten either position per project.

## Disposition of existing discussion

Before proposing anything, classify what the PR's conversation already settled. See `review-synthesizer` for the mechanics. The rubric's rules:

- **Settled** items (deferred with evidence, accepted as-is, declared intent) are never re-flagged on the PR without the user's explicit consent. They appear in the user-facing report with their evidence.
- **Open** items (unanswered, disputed) are fair game.
- Re-litigating a settled item is the worst failure mode this skill has. It tells the author the reviewer did not read the thread.

## Research basis

- Google eng-practices reviewer guide — approve-at-better standard, priority order, context reading, nit prefix, praise. <https://google.github.io/eng-practices/review/reviewer/>
- Conventional Comments — label/decorations vocabulary. <https://conventionalcomments.org/>
- Dan Lew, "Stop Nitpicking in Code Reviews" — signal-to-noise, automate the nits. <https://blog.danlew.net/2021/02/23/stop-nitpicking-in-code-reviews/>
- Mads Nedergaard, "Principles for code reviews" — approve optimistically and its caveats, nitpick carve-outs. <https://www.madsnedergaard.dk/thoughts/principles-for-code-reviews>
- Bacchelli & Bird, ICSE 2013 — reviews are knowledge transfer first; understanding is the hard part.
- Sadowski et al., ICSE 2018 — education and norm-keeping as review's everyday functions.
