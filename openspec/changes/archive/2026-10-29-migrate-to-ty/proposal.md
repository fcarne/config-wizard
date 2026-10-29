# Proposal

## Why

mypy is the last type checker left from the pre-uv toolchain, and it checks the project weakly: its pre-commit hook runs in an isolated environment with `--ignore-missing-imports`, so the Streamlit backend is checked against untyped Streamlit and the project environment's own mypy reports 11 errors the hook never shows. ty is Astral's type checker, the same family as ruff and uv. On a scratch clone of `main`, ty 0.0.95 reports 36 diagnostics, identical to 0.0.91 across five releases, it understands Pydantic models natively (it caught all five mistakes in a probe where the mypy plugin caught three), and it runs in about 0.6 seconds. Its official VS Code extension exists, and with uv now the package manager its environment detection works without extra configuration.

## What Changes

- Replace mypy with ty: add `ty` to the `dev` group pinned exactly, remove `mypy` from it, remove the `mirrors-mypy` hook and the `[tool.mypy]` table.
- Add a local pre-commit hook that runs `uv run --all-extras ty check`, so ty uses the lock-pinned environment with every extra installed and gives the same result everywhere. Point `make lint` at it.
- Configure ty in `pyproject.toml`: one file-scoped override for `config_wizard/schema.py` that turns off the two rules its inheritance pattern trips (`invalid-mutable-override` and `invalid-attribute-override`), and `unused-ignore-comment` as an error, which replaces mypy's `warn_unused_ignores`.
- Reach zero diagnostics: 16 narrow inline `# ty: ignore[rule]` comments cover the 17 remaining diagnostics (15 lines in `streamlit.py`, 1 in `tests/test_schema.py`), and the 13 existing `# type: ignore[code]` comments, which ty does not recognize, are removed.
- Give ty its own Dependabot group so a ty release arrives as a separate pull request.
- Update `AGENTS.md`, `CONSTITUTION.md`, the `uv run mypy*` permission in `.claude/settings.json`, and the devcontainer, which swaps `ms-python.mypy-type-checker` for the official `astral-sh.ty` extension.
- No runtime behavior changes. Source edits are comments only.

## Capabilities

### New Capabilities

None. This change is tooling only, so it sets `skip_specs: true`.

### Modified Capabilities

None. No requirement in `openspec/specs/` mentions the type checker.

## Impact

- Configuration: `pyproject.toml`, `uv.lock`, `.pre-commit-config.yaml`, `Makefile`, `.github/dependabot.yml`.
- Devcontainer: `devcontainer.json`, replacing one extension.
- Documents: `AGENTS.md`, `CONSTITUTION.md`, `.claude/settings.json`, and `ROADMAP.md`, which loses this item and has the type-checker mention in `add-ci-pipeline` updated.
- Code: suppression comments only, in `config_wizard/schema.py`, `config_wizard/backends/streamlit.py` and `tests/test_schema.py`.
- Out of scope, each its own change on `ROADMAP.md`: fixing the typing smells in `streamlit.py` (`fix-streamlit-collections` and `test-streamlit-backend`), redesigning `ResolvedSchema` so its overrides are sound, and CI (`add-ci-pipeline`). Pyrefly is only a fallback if ty fails, not part of this change.
