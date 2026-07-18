# Documentation conventions

This document defines the authoring conventions for files under `docs/`. It serves two readers: humans who land mid-tree from a link or search result, and AI systems that read each file as an isolated chunk. Every rule below exists for at least one of them. The research basis for these conventions is at the end of the file.

---

## Part 1: Layers and modes

### The two layers

The skill-standards wiki holds two kinds of content:

- **Universal fundamentals**: rules and principles any skill must satisfy to work, regardless of which architecture it follows. They live in `skill-standards/fundamentals/core/`.
- **Proposed architecture**: this repo's opinionated framework for building skills — conductors, building blocks, adapters, context reports. It lives in `skill-standards/fundamentals/architecture/`, `skill-standards/patterns/`, and `docs/manifestos/`.

The distinction matters because the layers make different kinds of claims. Fundamentals state invariants: "a skill must declare its invocation mode." Architecture docs argue a position: "we split conductors from workers." A reader must always know which kind of claim they are reading, and location alone does not tell them — an AI chunk carries no tree position, and a human landing mid-wiki sees a page, not a path.

### Every doc declares its layer and mode

State both in the lead block at the top of the file:

```markdown
## At a glance

**Layer:** proposed architecture. **Mode:** reference.
```

The mode is one of four:

| Mode | Job | Home |
|------|-----|------|
| Rule | States a norm the wiki holds | `fundamentals/`, `patterns/` |
| Guide | Walks through a task | `guides/` |
| Reference | Lookup material: field tables, schemas, glossary | `reference/`, `schemas/` |
| Explanation | Says why something is the way it is | `fundamentals/`, `manifestos/` |

One mode per file. When a file starts serving a second mode, move one mode's content to its canonical home and leave a pointer. A fundamentals page that grows field tables is drifting into reference; a reference page that grows rationale is drifting into explanation. This is the failure that put restated requirements into `fundamentals/core/structure/frontmatter.md` and an inline copy of the schema into `reference/format.md`; both were fixed by returning each file to its mode.

The mode also decides placement. A new doc's directory follows from its mode, not from where the author happened to be standing.

---

## Part 2: Structure

### One file, one focused point

Every document has a single, clear purpose. If a file is doing more than one thing, split it.

### Standalone topic

A simple topic that does not need sub-topics is a single markdown file at the appropriate level.

```text
fundamentals/architecture/tooling-awareness.md
```

### Topic with sub-topics

When a topic needs sub-topics, make it a directory with the landing page as `README.md`. The sub-topics are sibling files inside that directory.

```text
topic-name/
├── README.md              # landing page for the topic
├── sub-topic-one.md       # simple sub-topic: stays a single file
└── sub-topic-two/         # complex sub-topic: becomes its own directory
    ├── README.md          # landing page for the nested topic
    ├── aspect-a.md
    └── aspect-b.md
```

A sub-topic that is simple stays a single file. A sub-topic that itself needs sub-topics becomes a directory with its own `README.md`. Nesting stops when every file has one clear point.

### Directory landing pages

Every directory that is linked to must contain a `README.md`. That `README.md` is the canonical entry point for the directory.

A landing page `README.md` maps what is inside the directory. It links to each sibling file or subdirectory. It does not give detailed advice, reading-order instructions, or duplicate content that belongs in a child file.

A top-level `README.md` must enumerate every sibling directory at its level. Do not omit a directory that is part of the tree.

```text
skill-standards/
├── README.md          # links to fundamentals/, patterns/, guides/, reference/, schemas/
├── fundamentals/
│   ├── README.md      # links to core/ and architecture/
│   ├── core/
│   │   └── README.md  # links to each core topic
│   └── architecture/
│       └── README.md  # links to each architecture topic
├── patterns/
│   └── README.md
├── guides/
│   └── README.md
├── reference/
│   └── README.md
└── schemas/
    └── README.md
```

### Reading paths live at the topic level

Reading-order advice belongs in the directory that contains the topics. A parent `README.md` points to the child directories; the child `README.md` files contain the sequence for their own contents.

For example, the order in which to read core topics belongs in `fundamentals/core/README.md`, not in `fundamentals/README.md`.

### Why this structure

- **Predictable navigation:** any directory can be opened and its entry point is `README.md`.
- **Lean files:** each file focuses on one point, making it easier to read and maintain.
- **Scalability:** topics can grow from a single file into a directory without reorganizing the whole tree.
- **Clear ownership:** every concept has one authoritative location, so drift and duplication are easier to detect.

---

## Part 3: Page anatomy and prose

### Lead with the answer

Every doc opens with a lead block: what this file is, who should read it, and the verdict or rule. Most readers never finish a page, so the conclusion comes first and the detail after. The "At a glance" block in `skill-standards/reference/format.md` is the model.

### Sections stand alone

A reader or an AI chunker can land on any section without reading the ones before it.

- No "as mentioned above," "now that you've," or "with everything configured."
- Use explicit nouns over pronouns when the referent is more than a sentence away.
- Keep a constraint next to the rule it constrains. Chunk boundaries fall where they fall; proximity is the only guarantee that a rule and its limit travel together.

### Write to be scanned

- Headings state what the section settles, not a clever label.
- One idea per paragraph. A second idea in the same paragraph is usually skipped.
- Short paragraphs beat long nested lists.
- Cut half the words of a first draft, then check whether anything was lost.

### Voice

Docs use a human voice: plain, specific, intentional, written by a maintainer rather than an assistant.

- Em dashes are fine occasionally; they become a tic when every other sentence uses one.
- No hedge phrases: "it is important to note," "in conclusion," "in summary," "additionally," "as a reminder."
- No vague intensifiers: "robust," "seamless," "comprehensive," "crucial," "vital," "transformative," "profound," "deep."
- No abstract verbs: "delve," "elucidate," "navigate," "underscore," "shed light on," "foster," "leverage."
- No meta-narrative: "we will explore," "this guide aims to," "the goal is to," "let's break this down."
- No bullet-point sermons. Prefer short paragraphs to long nested lists.
- No tidy conclusions. End with the next step or the reference material, not a summary.
- Be specific. Use concrete terms, proper nouns, and exact paths. Avoid generic examples.
- Have a point of view. Docs record this repo's actual decisions, not an aggregate of every possible approach.
- Vary sentence length. Human writing mixes short and long sentences.

If a sentence could appear in an AI-generated article, rewrite it.

---

## Part 4: Examples and terminology

### Every rule pairs with an example

A normative rule without a worked example leaves room for interpretation, and interpretation drifts between readers. Pair each rule with a concrete example. Where contrast clarifies, show strong and weak side by side; the description examples in `skill-standards/reference/format.md` are the model.

Examples use real names, real paths, and real values — never `foo`, `bar`, or "something here."

### Coined terms go in the glossary

When the wiki coins a term ("reach clause," "context pointer," "leading word"), define it once in `skill-standards/reference/glossary.md`, then use it with no synonym drift. If four documents use a term and none define it, the term does not exist as far as the reader is concerned. This was the "reach clause" bug: referenced in four docs, defined in none.

---

## Part 5: Ownership, sync, and sources

### Canonical ownership

When a concept appears in more than one document, choose one canonical home for the full explanation. Other documents may mention the concept briefly and link to the canonical home.

Cross-links are encouraged. Cross-duplication of explanations is not.

### Orienting duplication is allowed; explanation duplication is not

A doc may repeat enough context to orient a reader who arrived cold — a sentence or two, no more. It may not restate the full explanation. The model is Wikipedia's summary style: the child article stands alone, and the parent keeps a summary plus a link, not a copy.

### Sync discipline

When the canonical home changes, the same edit updates its pointers. When a pointer section grows real content, move the content back to the canonical home. New material enters at the canonical home first; summaries are re-derived from it, never edited independently.

### Research basis sections

Any doc that makes claims about harnesses, models, or the wider ecosystem ends with a `## Research basis` section. Each entry links its source and states what is borrowed. Claims original to this repo say so. Long or numerous citation lists collect in `skill-standards/reference/sources.md`.

Format:

```markdown
## Research basis

- [What is borrowed], from [source](URL): [what it contributes].
- [What is original]: original to this repo, [one-line rationale].
```

### Linking

Use relative links. When a file moves, update both the file and any links pointing to it. Reference links must resolve.

Directory links rely on the target directory having a `README.md`. If a directory link is broken because the landing page is missing, add the `README.md` rather than changing the link to a specific file.

---

## Research basis

- One mode per document, from [Diátaxis](https://diataxis.fr/foundations/): the four modes derived from two dimensions of craft (action/cognition, acquiring/applying).
- Lead-first pages, summary layering, self-contained articles, orienting duplication, sync discipline, from [Wikipedia: Summary style](https://en.wikipedia.org/wiki/Wikipedia:Summary_style) and [Wikipedia: MOS, Lead section](https://en.wikipedia.org/wiki/Wikipedia:Manual_of_Style/Lead_section).
- Conclusion-first prose, one idea per paragraph, scannability, short word counts, from Nielsen, [How Users Read on the Web](https://www.nngroup.com/articles/how-users-read-on-the-web/): 79% of test users scan rather than read; measured usability gains of 58% (concise), 47% (scannable), 27% (objective language), 124% (combined).
- Self-contained sections, explicit terminology, constraint-next-to-rule, from [kapa.ai, Writing best practices](https://docs.kapa.ai/improving/writing-best-practices): how retrieval systems chunk documentation and why chunks must stand alone.
- Rule-plus-worked-example pairing, from the worked-example effect: Sweller & Cooper (1985), *The use of worked examples as a substitute for problem solving in learning algebra*; Gerjets, Scheiter & Catrambone (2004).
- Original to this repo: the two-layer model (universal fundamentals vs proposed architecture), the layer/mode label in the lead block, and the mode-to-directory mapping.
