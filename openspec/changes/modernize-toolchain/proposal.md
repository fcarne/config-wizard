# Proposal

## Why

The development toolchain has measured gaps. `make install` runs plain `poetry install`, which selects no pytest, so a fresh clone cannot run the tests; ruff and mypy are not project dependencies, so `poetry run ruff` fails and `poetry run mypy` runs a global binary that cannot load the Pydantic plugin. The pytest settings table is misnamed, so its options never apply. Python 3.10, the minimum, reached end of life on 2026-10-01. The lock is about 14 months old, the pre-commit pins lag (ruff 0.12.5 against 0.17.2, mypy 1.17.0 against 2.4.0), and nothing proposes updates.

## What Changes

- Require Python `>=3.11,<4.0` and drop the 3.10 classifier, keeping 3.11 to 3.13.
- Add a `dev` dependency group (pytest, pytest-cov, pytest-mock, pre-commit, ruff, mypy) that `poetry install` installs by default, and remove the `dev` extra.
- Rename the `[tool.pytest.ini]` table to `[tool.pytest.ini_options]` so its options apply.
- Refresh `poetry.lock` within the current dependency bounds.
- Bump the pre-commit hook revisions and drop the pyupgrade hook, which Ruff's `UP` rules replace. Hooks stay isolated: they keep running from pre-commit's own environments.
- Select the Ruff rules `I`, `UP`, `B`, `SIM` and `PT`, and fix what they report, including one duplicated test case.
- Add a Dependabot configuration covering pip, pre-commit and devcontainers.
- Update the documents that state toolchain facts: `CONSTITUTION.md`, `AGENTS.md` and `openspec/config.yaml`.
- No runtime behavior changes. Source edits are limited to import order and equivalent simplifications.

## Capabilities

### New Capabilities

None. This change is tooling only, so it sets `skip_specs: true`.

### Modified Capabilities

None. No requirement in `openspec/specs/` mentions the toolchain.

## Impact

- Configuration: `pyproject.toml`, `poetry.lock`, `.pre-commit-config.yaml`, new `.github/dependabot.yml`.
- Documents: `CONSTITUTION.md`, `AGENTS.md`, `openspec/config.yaml`; `ROADMAP.md` loses item 1 when the change is archived.
- Code: formatting and equivalent simplifications in `config_wizard/` and `tests/`; one duplicate test case removed, taking the suite from 98 to 97 cases.
- Out of scope, each its own change on `ROADMAP.md`: replacing mypy with ty (`migrate-to-ty`), CI (`add-ci-pipeline`) and fixes for the known Streamlit defects. Also out of scope: raising the `openapi-pydantic` and `textual` bounds, the unused `docs` extra, strict mypy, running hooks from the project environment, and adding a Python 3.14 classifier before anything tests it.
