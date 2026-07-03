# Issue Tracker Adapters

This directory contains adapter docs for the issue trackers supported by `debrief`.

## Supported trackers

- [Jira](JIRA.md)
- [GitHub Issues](GITHUB.md)
- [Linear](LINEAR.md)
- [Manual fallback](MANUAL.md)

## Selection

`debrief` selects one primary tracker per debrief using `preferences.issue_tracker` in `{marker_dir}/config/debrief.yaml`. Set it to `auto` to let the skill detect the first available tracker, or choose one explicitly.

If no tracker is available, the skill uses the [manual fallback](MANUAL.md) path.
