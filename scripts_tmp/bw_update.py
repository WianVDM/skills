import re

p = 'skills/main/authoring/write-a-skill/references/BRANCH_WORKFLOWS.md'
t = open(p, encoding='utf-8').read()

# 1. Conventions: phase 0 note
t = t.replace(
"""## Conventions

- Each phase ends with a **completion criterion**.""",
"""## Conventions

- Every branch starts at **phase 0: objective map** (see [OBJECTIVE_MAP.md][objective-map]). Nothing downstream runs on an unconfirmed map.
- Each phase ends with a **completion criterion**.""")

# 2. Full gate: replace '#### 1. Clarify intent' section with phase 0
clarify = t.index('#### 1. Clarify intent')
clarify_end = t.index('#### 2. Explore alternatives')
t = (t[:clarify] +
"""#### 0. Objective map

**Why:** designing the wrong skill is expensive. The objective map is the confirmed foundation every later phase reads from.

Build the objective map with the user via the `map-objective` worker: prefill the nine fields from the request, present the whole map, and grill only the gaps. See [OBJECTIVE_MAP.md][objective-map] for the fields and protocol.

**Completion criterion:** the map is confirmed by the user and persisted to the intent note.

""" + t[clarify_end:])

# 3. Insert description design after '#### 5. Define scope' section
sel = t.index('#### 6. Select patterns')
t = (t[:sel] +
"""#### 6. Description design

**Why:** the description is the routing surface — the most important field in `SKILL.md`. It is designed, not filled in.

Draft the description from the objective map: leading word or domain first, one trigger per distinct branch from the map's triggers field, a reach clause if other skills consume the skill, ≤ 1024 characters. Present it to the user for confirmation before any drafting begins.

**Completion criterion:** the description follows the canonical shape and the user has confirmed it.

""" + t[sel:])

# 4. Renumber subsequent full-gate headings
t = t.replace('#### 6a. Pattern adherence', '#### 7a. Pattern adherence')
t = t.replace('#### 6b. Design capability-to-tool strategy', '#### 7b. Design capability-to-tool strategy')
for old, new in [('#### 11. Confirm and write', '#### 12. Confirm and write'),
                 ('#### 10. Generate evals', '#### 11. Generate evals'),
                 ('#### 9. Audit and validate', '#### 10. Audit and validate'),
                 ('#### 8. Draft artifacts', '#### 9. Draft artifacts'),
                 ('#### 7. Token justification', '#### 8. Token justification'),
                 ('#### 6. Select patterns', '#### 7. Select patterns')]:
    t = t.replace(old, new)

# 5. Quick gate list
quick_old = """1. **Clarify intent** (minimal) — capture problem, trigger, and success criteria.
2. **Explore alternatives** (light) — check existing skills and simple alternatives; run `detect-skill-overlap` for any close match and write the findings to `{context}/skill-design/{skill-name}-overlap-findings.md`.
3. **Decide shape and colocation** — name, description, invocation; decide whether to colocate inside an existing skill or extract as a new reusable skill; invoke `detect-skill-overlap` to flag extraction opportunities; present the user with reuse/colocate/extract options and record decisions in the decision log.
4. **Define scope** — one objective, in-scope, out-of-scope.
5. **Select patterns** — apply fundamentals.
6. **Pattern adherence** — confirm pattern mappings or deviations; warn if canonical docs are unavailable.
7. **Token justification** — defend the minimal artifact set; remove duplicates.
8. **Design capability-to-tool strategy** — for each load-bearing capability, note the preferred tool, fallback, and degraded-output disclosure.
9. **Draft** — write the skill files.
10. **Audit** — run `audit-skill` and `validate-skill-frontmatter`.
11. **Confirm and write** — get approval before writing."""
quick_new = """1. **Objective map** (minimal) — prefill the nine fields from the brief, confirm with the user.
2. **Explore alternatives** (light) — check existing skills and simple alternatives; run `detect-skill-overlap` for any close match and write the findings to `{context}/skill-design/{skill-name}-overlap-findings.md`.
3. **Decide shape and colocation** — name and invocation; decide whether to colocate inside an existing skill or extract as a new reusable skill; invoke `detect-skill-overlap` to flag extraction opportunities; present the user with reuse/colocate/extract options and record decisions in the decision log.
4. **Define scope** — one objective, in-scope, out-of-scope.
5. **Description design** — leading word, distinct triggers, reach clause, ≤ 1024 characters, confirmed.
6. **Select patterns** — apply fundamentals.
7. **Pattern adherence** — confirm pattern mappings or deviations; warn if canonical docs are unavailable.
8. **Token justification** — defend the minimal artifact set; remove duplicates.
9. **Design capability-to-tool strategy** — for each load-bearing capability, note the preferred tool, fallback, and degraded-output disclosure.
10. **Draft** — write the skill files.
11. **Audit** — run `audit-skill` and `validate-skill-frontmatter`.
12. **Confirm and write** — get approval before writing."""
assert quick_old in t, 'quick gate list not found'
t = t.replace(quick_old, quick_new)

# 6. Replace decide-gate section with explore branch section
decide_start = t.index('### Create branch — decide gate')
change_start = t.index('## Change branch')
t = (t[:decide_start] +
"""## Explore branch

The entry point for vague ideas and rough drafts. The output is a confirmed objective map and a recommendation — never files.

### 1. Objective map

Build the map with the user via `map-objective` (prefill-and-confirm; grill the gaps). See [OBJECTIVE_MAP.md][objective-map].

**Completion criterion:** the map is confirmed and persisted to the intent note.

### 2. Explore what exists

Run `list-available-skills`, `search-skills-registry`, and `detect-skill-overlap`. Write overlap findings to `{context}/skill-design/{skill-name}-overlap-findings.md`.

**Completion criterion:** the alternatives report exists and the user has seen the top findings.

### 3. Resolve the shape (if unclear)

If the open question is shape — skill, script, MCP server, context file, or existing skill — invoke `decide-skill-shape` and consume its decision report. Do not leave the branch.

**Completion criterion:** the shape is confirmed, or the user accepts a recommendation to revisit later.

### 4. Recommend

Present one of four outcomes with reasoning:

- **Build it** — hand the confirmed map to the `create` branch.
- **Reuse or extend** — name the existing skill and show the fit.
- **Simpler answer** — a script, MCP server, context file, or rule.
- **Not worth it** — record why; nothing is written.

**Completion criterion:** the user has confirmed the recommendation; no files were written.

""" + t[change_start:])

# 7. Change branch: comprehension confirmation + renumber
t = t.replace(
"""2. Comprehend the skill using the review principles.
3. Produce an incomplete report if the core questions cannot be answered.""",
"""2. Comprehend the skill using the review principles.
3. Confirm the comprehension brief with the user — scoring does not start on an unconfirmed understanding.
4. Produce an incomplete report if the core questions cannot be answered.""")
t = t.replace(
"""4. Run `audit-skill` and `validate-skill-frontmatter`.
5. Produce a structured, verdict-led audit report that incorporates the review principles.
6. For the `update` gate, produce a remediation plan, confirm each change, apply approved changes, and run a final audit.""",
"""5. Run `audit-skill` and `validate-skill-frontmatter`.
6. Produce a structured, verdict-led audit report that incorporates the review principles.
7. For the `update` gate, produce a remediation plan, confirm each change, apply approved changes, and run a final audit.""")

# 8. Initialize: capability_index_path
t = t.replace(
"""- `standards_path`: path to the canonical skill standards directory.
- `registries`: list of skill registries to search.""",
"""- `standards_path`: path to the canonical skill standards directory.
- `capability_index_path`: path to the machine-readable capability index (project-local override or bundle default).
- `registries`: list of skill registries to search.""")

# 9. Link definition
t = t.replace('[fundamentals]: FUNDAMENTALS.md',
              '[objective-map]: OBJECTIVE_MAP.md\n[fundamentals]: FUNDAMENTALS.md')

open(p, 'w', encoding='utf-8').write(t)
print('BRANCH_WORKFLOWS.md updated')
