---
description: |
  Detects documentation that is out of sync with recent code changes and opens a
  draft pull request with updates.
on:
  schedule: daily on weekdays
  workflow_dispatch:
permissions:
  contents: read
  issues: read
  pull-requests: read
  copilot-requests: write
strict: true
network:
  allowed:
    - defaults
    - python
tools:
  github:
    mode: gh-proxy
    toolsets: [default]
safe-outputs:
  create-pull-request:
    title-prefix: "[docs-sync] "
    draft: true
    allowed-files:
      - "Readme.md"
---

# Docs Sync PR

## Task

Review recent repository code changes and compare them with the current documentation in `Readme.md`.
Focus on user-facing behavior, setup, configuration, endpoints, and examples described by the repository.

If the documentation is already consistent with the recent code state, call `noop` with a short explanation.

If updates are needed:

1. Make the smallest accurate documentation-only edits to `Readme.md`.
2. Do not change source code, infrastructure, or generated files.
3. Keep the existing language, tone, and structure unless a small clarification is necessary.
4. Summarize what was out of sync and what you updated.
5. Create a draft pull request using the configured safe output.

## Validation

- Base your conclusions on actual repository files and recent commit history.
- Prefer recent commits when deciding what is "out of sync".
- Do not invent features or configuration that are not present in the code.
- Use `noop` instead of opening a PR when no documentation change is required.
