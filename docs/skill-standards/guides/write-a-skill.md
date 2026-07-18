# Write a skill

**Layer:** proposed architecture. **Mode:** guide.

1. Read [what-is-a-skill][what-is-a-skill] and [types][types].
2. Choose the right type: building block, conductor, or wrapper.
3. Draft the smallest viable `SKILL.md` using [format][format] and [structure][structure].
4. Write the `description` as a routing surface: front-load the leading word or domain, list one trigger per distinct branch, and add a reach clause if other skills consume it. See [format][format].
5. Declare dependencies and design the capability-to-tool strategy using [dependencies and bundling][dependencies] and [tooling awareness][tooling-awareness].
6. Check [common mistakes][common-mistakes] before expanding, especially the guidance on premature extraction and bloat.
7. Decide whether the capability belongs inside an existing skill or should be extracted as a separate building block using the principle in [building-block pattern][building-block] and [architecture manifesto][architecture].
8. If the skill is global, configurable, stateful, report-producing, reusable, or versioned, read the relevant pattern docs in [patterns][patterns].
9. Review against [evaluation][evaluation]. For practical testing, see [trigger evals][trigger-evals] and [context budget][context-budget].

[what-is-a-skill]: ../fundamentals/core/what-is-a-skill/README.md
[types]: ../fundamentals/architecture/types/README.md
[format]: ../reference/format.md
[structure]: ../fundamentals/core/structure/README.md
[dependencies]: ../fundamentals/architecture/dependencies-and-bundling.md
[tooling-awareness]: ../fundamentals/architecture/tooling-awareness.md
[common-mistakes]: ../fundamentals/core/common-mistakes/README.md
[building-block]: ../patterns/building-block.md
[architecture]: ../../manifestos/architecture.md
[patterns]: ../patterns/README.md
[evaluation]: ../fundamentals/architecture/evaluation.md
[trigger-evals]: ./trigger-evals.md
[context-budget]: ../fundamentals/core/context-budget.md
