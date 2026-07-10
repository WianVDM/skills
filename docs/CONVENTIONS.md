# Documentation conventions

This document defines the structural and authoring conventions for files under `docs/`.

---

## One file, one focused point

Every document should have a single, clear purpose. If a file is doing more than one thing, split it.

---

## Standalone topic

A simple topic that does not need sub-topics is a single markdown file at the appropriate level.

```text
fundamentals/architecture/tooling-awareness.md
```

---

## Topic with sub-topics

When a topic needs sub-topics, make it a directory with the landing page as `README.md`. The sub-topics are sibling files inside that directory.

```text
topic-name/
├── README.md              # landing page for the topic
├── sub-topic-one.md     # simple sub-topic: stays a single file
└── sub-topic-two/         # complex sub-topic: becomes its own directory
    ├── README.md          # landing page for the nested topic
    ├── aspect-a.md
    └── aspect-b.md
```

A sub-topic that is simple stays a single file. A sub-topic that itself needs sub-topics becomes a directory with its own `README.md`. Nesting stops when every file has one clear point.

---

## Directory landing pages

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

---

## Reading paths live at the topic level

Reading-order advice belongs in the directory that contains the topics. A parent `README.md` points to the child directories; the child `README.md` files contain the sequence for their own contents.

For example, the order in which to read core topics belongs in `fundamentals/core/README.md`, not in `fundamentals/README.md`.

---

## Canonical ownership

When a concept appears in more than one document, choose one canonical home for the full explanation. Other documents may mention the concept briefly and link to the canonical home. Do not duplicate the full explanation.

Cross-links are encouraged. Cross-duplication is not.

---

## Why this structure

- **Predictable navigation:** any directory can be opened and its entry point is `README.md`.
- **Lean files:** each file focuses on one point, making it easier to read and maintain.
- **Scalability:** topics can grow from a single file into a directory without reorganizing the whole tree.
- **Clear ownership:** every concept has one authoritative location, so drift and duplication are easier to detect.

---

## Linking

Use relative links. When a file moves, update both the file and any links pointing to it. Reference links must resolve.

Directory links rely on the target directory having a `README.md`. If a directory link is broken because the landing page is missing, add the `README.md` rather than changing the link to a specific file.
