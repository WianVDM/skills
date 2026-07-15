# Dependencies

## Required skills

- `worker-contract` — provides the standard return format and forbidden actions.

## Required capabilities

- Model reasoning to compare findings against natural-language scope.

## Optional inputs

- `project_conventions`: list of project conventions to include in scope.
- `acceptance_criteria`: list of acceptance criteria strings.
- `changed_files`: list of changed file paths.

## No runtime tools

This subagent does not invoke tools by default. It reads the scope and findings provided in the prompt.
