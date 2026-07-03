# Implementer

## Purpose

Generic implementation fallback when no preferred implementation skill is available.

## Inputs

- Ticket key.
- Current phase contract.
- State.md, plan.md, decisions.md, assumptions.md.
- Project coding standards path.

## Process

1. Read the phase contract and identify the required changes.
2. Read relevant source files.
3. Make minimal, focused changes.
4. Follow project coding standards.
5. Add or update tests if the project requires it.
6. Run verification steps defined in the phase contract.

## Outputs

- Files modified.
- Summary of changes.
- Verification results.
- Any new gaps discovered.
