# Worked examples

## Skill vs script

### Problem

"I want to rename all `snake_case` variables to `camelCase` in a TypeScript file."

### Classification

1. **Repetition and judgment** — The transformation is narrow and deterministic: input is a file, output is the same file with renamed identifiers. No domain judgment is required. → **Lean toward script**.
2. **Trigger mode** — The user will invoke it explicitly when needed. → **Either script or skill**.
3. **Coordination scope** — Single focused capability: parse TypeScript, rename identifiers, write file. → **Either script or building-block skill**.
4. **Artifact nature** — The output is a deterministic file transformation. → **Script**.

### Recommendation

**Script**. The task is deterministic, narrow, and does not require the reusable contract or model-invocation surface of a skill. A one-off `rename-to-camelcase.ts` script is the lighter solution.

### Alternative

If the user later wants the agent to autonomously detect inconsistent naming and apply the rename, the capability should be promoted to a **building-block skill** that wraps the script and exposes a clear trigger.
