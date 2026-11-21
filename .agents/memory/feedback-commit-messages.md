---
name: feedback-commit-messages
description: "Commit messages are a single subject line only: no body, no description, no Co-Authored-By trailer"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 4d1e8bfa-82c0-4fde-80bc-19fb06dd817c
  modified: 2026-10-25T21:03:56.250Z
---

Commit messages in this project are message only: one subject line, no body or description, and no `Co-Authored-By` trailer.

**Why:** the user wants to use fewer tokens. It overrides the default attribution lines the harness suggests for commits.

**How to apply:** use `git commit -m "<gitmoji> <subject>"` (the repo uses gitmoji-prefixed subjects). Pull request descriptions are not covered by this rule. The same rule goes into AGENTS.md (task 3.1 of the `baseline-existing-capabilities` change). See [[project-openspec-baseline]].
