# Proposal

## Why

The toolchain is moving to Astral's tools: ruff is already in use, ty is next, and the official ty pre-commit hook is built on `uv check`. A trial on a scratch copy of `main` showed uv fits the project as it is. `uv lock` resolved 97 packages from the unchanged `pyproject.toml`, and all 11 key packages (pydantic 2.14.1, Streamlit 1.66.1, ruff 0.17.2 and the rest) matched `poetry.lock`; `uv sync` built the environment in about 8 seconds from cold; 97 tests passed. uv also provides `uv audit`, which found pytest 8.4.2 affected by CVE-2025-71176 (fixed in 9.0.3), a fix our `<9.0.0` bound blocks. Moving the package manager first keeps the ty change small and lets its hook use the tracked uv lock.

## What Changes

- Replace Poetry with uv: add a tracked `uv.lock`, remove `poetry.lock`, and leave the dependency tables in `pyproject.toml` as they are.
- Widen the `pytest` and `pytest-cov` bounds so the advisory is fixed instead of ignored. The trial passed all 97 tests on pytest 9 with pytest-cov 7.
- Adjust two existing hooks so the tracked lock passes them: exclude `uv.lock` from the large-file check (the lock is 518 KB against a 500 KB limit) and drop `toml` from the ruff hooks' file types, since ruff lints Python only.
- Add the `uv-lock` and `uv-audit` hooks from `astral-sh/uv-pre-commit`, pinned to the uv version. Both run only when `uv.lock` or `pyproject.toml` change.
- Run pre-commit through `uv run`, so the hooks use the lock-pinned pre-commit. The isolated ruff and mypy hook environments are unchanged.
- Update the `Makefile`: `make install` runs `uv sync` and `make update` refreshes the lock.
- Update the devcontainer: drop the Poetry feature and its environment variables, and install uv with pipx.
- Switch the Dependabot `pip` ecosystem to `uv`.
- Update `README.md`, `AGENTS.md`, `CONSTITUTION.md` and `.claude/settings.json` to the uv commands.
- Replace the `poetry-core` build backend with `uv_build`, configured for the flat layout, and move the license metadata to the PEP 639 form (`license = "MIT"`, `license-files`, no license classifier). Building both ways showed identical package files and the same dependency metadata.
- No runtime behavior changes.

## Capabilities

### New Capabilities

None. This change is tooling only, so it sets `skip_specs: true`.

### Modified Capabilities

None. No requirement in `openspec/specs/` mentions the toolchain.

## Impact

- Configuration: `pyproject.toml` (two bounds, the build system and the license fields), new `uv.lock`, removed `poetry.lock`, `.gitignore`, `.pre-commit-config.yaml`, `.github/dependabot.yml`, `Makefile`.
- Devcontainer: `devcontainer.json`, `devcontainer-lock.json`, `post-create.sh`.
- Documents: `README.md`, `AGENTS.md`, `CONSTITUTION.md`, `.claude/settings.json`.
- Contributors: existing clones need `rm -rf .venv && uv sync`, and need uv installed locally.
- Out of scope, each its own change: replacing mypy with ty (`migrate-to-ty`, which comes next and will use uv), CI (`add-ci-pipeline`, which adds `setup-uv` and the `github-actions` ecosystem), a `.python-version` file, and the unused `docs` extra.
