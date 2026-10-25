# Design

## Context

See `proposal.md` for motivation. Current state, with the evidence gathered while exploring:

| # | Issue | Evidence |
|---|-------|----------|
| 1 | A fresh clone cannot run tests after `make install` | `poetry install --dry-run` selects 0 pytest or Streamlit packages; `dev` is an extra, installed only with `--extras` or `--all-extras` |
| 2 | ruff and mypy are not project dependencies | `poetry run ruff` reports "Command not found"; `poetry run mypy` runs `/usr/local/py-utils/bin/mypy` 1.16.1, which fails with `No module named 'pydantic'` while loading the plugin |
| 3 | pytest options never apply | The table is `[tool.pytest.ini]`; plain `pytest tests` prints no coverage |
| 4 | Python 3.10 is end of life | `endoflife.date`: 3.10 on 2026-10-01, 3.11 on 2027-10-31, 3.12 on 2028-10-31 |
| 5 | Hook pins lag | ruff-pre-commit v0.12.5 (latest v0.17.2), mirrors-mypy v1.17.0 (v2.4.0), pre-commit-hooks v5.0.0 (v6.0.0), pyupgrade v3.20.0 (v3.22.0) |
| 6 | The lock is untracked and stale | `.gitignore` line 108 ignores `poetry.lock` and `git ls-files` lists no lock, so it was never committed; the local copy is old: `poetry update --dry-run` moves pydantic 2.11.7 to 2.14.1, pydantic-core 2.33.2 to 2.50.1, typing-extensions 4.14.1 to 4.16.0, jsonschema 4.25.0 to 4.26.0, pydantic-settings 2.10.1 to 2.16.1; extras (Streamlit 1.48 to 1.66, pytest 8 to 9) also lag |
| 7 | Ruff's default rule set depends on its version | ruff 0.12.5 defaults reported 0 findings; ruff 0.17.2 enables 407 rules by default, including parts of `I`, `UP`, `B`, `SIM` and `PT`, and reports 23 findings: 18 autofixed (import order and `typing_extensions.Any`) and 5 left (3 `SIM103`, 1 `SIM102`, 1 `PT014`); adding the whole families gives 14 findings in total, the extra 9 being 7 `PT006`, 1 `SIM108` and 1 `UP042` |
| 8 | No update bot | `.github/` is empty |

Constraints that shape the approach:
- `pre-commit` runs ruff and mypy from its own isolated environments, and its mypy hook passes `--ignore-missing-imports`, so the Streamlit backend is currently checked against untyped Streamlit.
- The package is not published (PyPI returns 404), so removing an extra breaks no consumer.
- `poetry.lock` is git-ignored, so a fresh clone resolves the newest versions inside the bounds instead of a known set.
- The 98 tests cover the schema core only; the backends have none.
- Poetry 2.5.1 is installed here; the devcontainer installs the latest Poetry through its feature.

## Goals / Non-Goals

**Goals:**
- `make install` yields a working development environment from a fresh clone.
- Every tool named in `AGENTS.md` and `.claude/settings.json` runs through `poetry run`.
- The toolchain is current, and stays current through automated update pull requests.
- No runtime behavior change.

**Non-Goals:**
- Changing which type checker runs. mypy stays; the swap is `migrate-to-ty`.
- Changing what mypy sees. Hooks stay isolated.
- Bumping `openapi-pydantic` past 0.5 or `textual` past 5, which need their own compatibility checks.
- Test coverage or CI, which have their own roadmap items.

## Decisions

### Development tools live in a dependency group
Add `[dependency-groups] dev` with pytest, pytest-cov, pytest-mock, pre-commit, ruff and mypy. Poetry installs groups by default, so plain `poetry install` gives a complete environment (issue 1, issue 2). Verified by a fresh install in a task, since support in the installed Poetry is assumed from its documentation.

Alternative: keep `dev` as an extra. Rejected: extras are opt-in, so `make install` would still lack the tools, and `--all-extras` also pulls Streamlit, Typer, Textual and mkdocs.

### The `dev` extra is removed
The package is unpublished, so no consumer can depend on `config-wizard[dev]`. The unused `docs` extra is left alone until documentation exists.

### Hooks stay isolated
`pre-commit` keeps running ruff and mypy from remote hook repositories with the current `--ignore-missing-imports` behavior. Ruff and mypy are therefore pinned twice, once as hook revisions and once in the lock, and Dependabot updates both.

Alternative: local hooks that call `poetry run ruff` and `poetry run mypy`, giving one version source. Rejected for this change: mypy would then see Streamlit's real types and likely report new errors, which overlaps with triaging ty's diagnostics. `migrate-to-ty` revisits it when the checker changes anyway.

### Python 3.11 is the floor
`requires-python` becomes `>=3.11,<4.0` and the 3.10 classifier goes. Ruff reads its target version from `requires-python`, so no separate setting is added, and the pyupgrade hook with `--py310-plus` is dropped. Classifiers keep 3.11 to 3.13; 3.14 waits for CI to test it.

Alternative: 3.12, matching the devcontainer. Rejected: 3.11 is supported until 2027-10-31 and nothing in the code needs 3.12.

### Ruff extends its defaults with `I, UP, B, SIM, PT` and findings are fixed, not ignored
Ruff 0.17's own defaults are far wider than 0.12's, so selecting only the planned families would narrow coverage. `[tool.ruff.lint] extend-select = ["I", "UP", "B", "SIM", "PT"]` keeps the whole of those families enabled whatever the defaults do in later versions, and leaves every other default rule on. Behavior preservation rules:
- `SIM103` on the three Streamlit button helpers is rewritten to the equivalent boolean expression. `_is_clear_button_disabled` stays inverted (known issue 7 in the archived baseline design) and is fixed by `fix-streamlit-collections`, not here.
- `PT014` removes the second `(Schema(type=DataType.NULL), InputType.NULL)` case in `tests/test_mapper.py`, which is identical to an earlier one. The suite goes from 98 to 97 cases.
- `UP042` converts `InputType(str, Enum)` to `StrEnum`. Equality with strings and construction from values are unchanged. In 3.11+, formatting changes: `f"{InputType.TEXT}"` yields `text` instead of `InputType.TEXT`. The only use is an f-string in an error path that normal use cannot reach, so the difference is accepted, and the conversion is its own commit so it can be reverted alone.
- No rule is disabled to make a finding go away. A finding that cannot be fixed equivalently is reported and decided by the user.

Alternatives: rely on the defaults alone, rejected because the policy would float with Ruff versions; or a fixed `select` of the defaults, rejected as a very long list that would still need maintaining.

### Dependabot over Renovate
GitHub's documentation lists Poetry v2, pre-commit hook revisions and devcontainers as supported ecosystems, and Dependabot needs no application install. With the lock tracked it updates the lock as well as the bounds. Configure pip, pre-commit and devcontainers on a weekly schedule with a small pull request limit and grouped minor and patch updates. `github-actions` is added by `add-ci-pipeline` once workflows exist.

Alternative: Renovate. Rejected: it needs an application installed on the repository and offers nothing this project needs yet.

### The lock is tracked
Remove `poetry.lock` from `.gitignore` (leaving `poetry.toml` ignored) and commit the lock, so every clone and CI run installs the same versions and Dependabot can update the lock itself. The current lock is committed first as a baseline, then refreshed in a separate commit so the refresh diff is reviewable and revertible.

Alternative: leave it untracked. Rejected: environments are not reproducible, new upstream releases only surface on a fresh install, and Dependabot could only bump the bounds in `pyproject.toml`. The cost of tracking is lock diffs in pull requests, and consumers of a library are unaffected by a lock.

### Lock refreshed within current bounds
Run `poetry update`, which re-locks core and extras together. Bounds are not widened. The 98 tests assert exact resolved schemas, so a Pydantic change in generated JSON Schema would show up as a failure. Streamlit has no tests, so its refresh is checked by running the README example under Streamlit's `AppTest` with the refreshed version.

## Risks / Trade-offs

- [Pydantic 2.14 changes generated JSON Schema] -> The exact-dict tests fail; investigate whether the change is semantic before touching an expectation, and pause if it is.
- [mypy 2.x reports new errors] -> Fix them equivalently; do not suppress. Pause if a fix would change behavior.
- [Ruff 0.17 reformats or flags more] -> Bump hooks in their own commit and review the diff size before applying rules. Realized: the new defaults flagged 23 findings immediately.
- [Ruff's other default rules can still shift with future bumps] -> `extend-select` pins the five families; changes in other defaults surface in the Dependabot pull request.
- [Streamlit 1.48 to 1.66 is covered only by a smoke test] -> Accepted; `test-streamlit-backend` is on the roadmap.
- [Two version sources for ruff and mypy can drift between update pull requests] -> Accepted; Dependabot updates the lock and the hook revisions, and `migrate-to-ty` revisits it.
- [Tracking the lock adds lock diffs to pull requests] -> Accepted for reproducibility; Dependabot groups limit the churn.
- [Weekly Dependabot pull requests add review load] -> Small pull request limit and grouped updates.

## Migration Plan

Land as separate commits in dependency order so each can be reverted alone: Python floor, dev group and pytest table, lock refresh, hook bumps, Ruff rules, Dependabot, documents. The lock is committed as a baseline before it is refreshed. Rollback: revert the commits; reverting the refresh commit restores the baseline lock.
