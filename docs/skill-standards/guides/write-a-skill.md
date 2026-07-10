# Write a skill

1. Read [what-is-a-skill][what-is-a-skill] and [types][types].
2. Choose the right type: building block, conductor, or wrapper.
3. Draft the smallest viable `SKILL.md` using [format][format] and [structure][structure].
4. Declare dependencies and design the capability-to-tool strategy using [dependencies and bundling][dependencies] and [tooling awareness][tooling-awareness].
5. Check [common mistakes][common-mistakes] before expanding, especially the guidance on premature extraction and bloat.
6. Decide whether the capability belongs inside an existing skill or should be extracted as a separate building block using the principle in [building-block pattern][building-block] and [architecture manifesto][architecture].
7. If the skill is global, configurable, stateful, report-producing, reusable, or versioned, read the relevant pattern docs in [patterns][patterns].
8. Review against [evaluation][evaluation]. For practical testing, see [trigger evals][trigger-evals] and [context budget][context-budget].

[what-is-a-skill]: ../fundamentals/core/what-is-a-skill/README.md
[types]: ../fundamentals/core/types/README.md
[format]: ../reference/format.md
[structure]: ../fundamentals/core/structure/README.md
[dependencies]: ../fundamentals/architecture/dependencies-and-bundling.md
[tooling-awareness]: ../fundamentals/architecture/tooling-awareness.md
[common-mistakes]: ../fundamentals/core/common-mistakes/README.md
[building-block]: ../patterns/building-block.md
[architecture]: ../../manifestos/architecture.md
[patterns]: ../patterns/README.md
[evaluation]: ../fundamentals/architecture/evaluation.md
[trigger-evals]: ../reference/trigger-evals.md
[context-budget]: ../reference/context-budget.md
