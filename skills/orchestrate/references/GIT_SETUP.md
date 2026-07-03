# Git Setup

Prepare the source-control workspace before orchestration.

## Check

1. Check for uncommitted changes.
2. Check current branch.
3. If on a protected branch and no feature branch exists, stop and ask the user.

## Setup

1. Fetch latest from the default remote.
2. Checkout the default base branch and pull latest.
3. Create or checkout the feature branch using the configured naming pattern.

## Rules

- Hard stop if uncommitted changes exist and the user has not resolved them.
- Branch name follows the configured pattern, defaulting to the ticket key.
- Never commit changes.
- Never push changes.
- Never checkout a protected branch as a feature branch.
