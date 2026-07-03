# Baseline Integration

The `baseline` skill is a **soft default building block** for `debrief`. It captures current UI, API, or code state and produces a report that the debrief can consume as evidence.

Baseline is not a hard dependency. When the ticket involves verifiable state, `debrief` should invoke baseline by default. If baseline is unavailable, the user must explicitly approve proceeding without it.

---

## When to invoke baseline

A ticket involves **verifiable state** when it describes something that can be observed, reproduced, or measured in the running system or codebase. Examples:
- UI behavior, bug reproduction, visual state.
- API response or error.
- Code-level output, test result, or performance metric.

Non-verifiable examples:
- Documentation changes.
- Process or policy decisions.
- Pure requirements clarification without implementation.

Use `detect-verifiable-state.py` or the task-type classifier to decide if baseline is relevant. Then apply the baseline mode rules:

| Mode | Verifiable state | Non-verifiable state |
|---|---|---|
| `required` | Invoke baseline. Stop if unavailable; ask user. | Consult user before skipping; do not skip silently. |
| `optional` | Invoke baseline. If unavailable, ask user. | Consult user before skipping; do not skip silently. |
| `skip` | Do not invoke baseline. | Do not invoke baseline. |

---

## Invoking the baseline skill

Treat baseline as a skill workflow, not a subagent with a made-up prompt. The main skill delegates invocation to the `baseline-invoker` subagent, which:

1. Passes the ticket key as the `scope` to baseline.
2. Uses the current branch as the default branch.
3. Includes the debrief's understanding of the ticket so baseline does not need to read the incomplete debrief report.

Example request to the baseline invoker:

```text
Run the baseline skill for scope {ticket-key} on the current branch.
Context: {brief summary of the ticket, expected behavior, and what to verify.}
```

This avoids circularity: baseline does not depend on the unfinished debrief document.

---

## Baseline report location

After baseline completes, read its canonical report:

```text
{context_dir}/baseline/{scope}-{branch}.md
```

- `{scope}` is usually the ticket key.
- `{branch}` is the current branch.

The debrief document references baseline artifacts from this location. Do not move or copy baseline artifacts into the debrief directory.

---

## Handling `needs_input`

If baseline returns `needs_input` (for example, authentication, dev server URL, or environment choice):

1. Surface the exact question to the user.
2. Record the answer in config notes or state if it is reusable.
3. Retry the baseline skill with the provided information.
4. Do not let baseline ask the user directly.

---

## Handling baseline failure

If baseline fails and cannot proceed:

1. Stop generating the debrief document.
2. Explain the failure to the user.
3. Present options:
   - **Retry** — try baseline again after the user has fixed the environment.
   - **Fix config** — open the relevant config and adjust it.
   - **Proceed without baseline** — continue the debrief, noting baseline unavailable. Requires explicit user approval.
   - **Abort** — stop the debrief and wait for user direction.
4. Wait for the user to choose. Do not choose an option yourself.

---

## Optional mode and clearly irrelevant tickets

If `baseline_mode: optional` and the ticket clearly does not involve verifiable state (for example, a pure documentation or policy question), consult the user before skipping baseline. Document the decision.

---

## Failure handling summary

| Scenario | Action |
|----------|--------|
| Baseline required and succeeds | Continue debrief normally. |
| Baseline required and `needs_input` | Ask user, record answer, retry. |
| Baseline required and fails | Present options; only proceed with explicit approval. |
| Baseline optional and relevant | Invoke baseline; consult user if it cannot run. |
| Baseline optional and not relevant | Consult user before skipping. |

---

## Absorbing baseline findings

After baseline completes, extract:

- Baseline status (`complete`, `failed`, `skipped`, etc.).
- Whether the bug is reproducible (for bug baselines).
- Key screenshots or artifacts.
- Console/network errors.
- Deviations from the debrief description.

Record these in:

- `{context_dir}/debrief/{key}/state.md` under `## Baseline Status`.
- The debrief document under `## Baseline Status`.
