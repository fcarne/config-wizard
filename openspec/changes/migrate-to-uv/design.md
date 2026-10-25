# Design

## Context

See `proposal.md` for motivation. Evidence from a scratch clone of `main` with uv 0.13.5; nothing in the repository was touched:

| # | Finding | Evidence |
|---|---------|----------|
| 1 | uv fits `pyproject.toml` unchanged | `uv lock` resolved 97 packages; pydantic, pydantic-core, streamlit, pytest, ruff, mypy, jsonschema, typing-extensions, openapi-pydantic, textual and typer had identical versions in `uv.lock` and `poetry.lock` |
| 2 | The environment and tests work | `uv sync` took 8.5 s from cold and installed the `dev` group by default; `--all-extras` added Streamlit 1.66.1; `pytest tests` reported 97 passed |
| 3 | `uv audit` works but is experimental | It prints an experimental warning, accepts `--preview-features audit-command`, queries OSV, supports `--ignore` and `--ignore-until-fixed`, and exits 1 when it finds something |
| 4 | The first audit finding is real | pytest 8.4.2 is affected by CVE-2025-71176 (PYSEC-2026-1845), fixed in 9.0.3; the `<9.0.0` bound blocks the fix; the suite also passes (97) on pytest 9 with pytest-cov 7 |
| 5 | Official hooks exist | `astral-sh/uv-pre-commit` 0.13.5 provides `uv-lock`, `uv-sync` and `uv-audit`; the lock and audit hooks run only when `uv.lock`, `pyproject.toml` or `uv.toml` change |
| 6 | Dependabot supports uv | GitHub's ecosystem list includes `uv` next to `pre-commit` and `devcontainers` |
| 7 | No official devcontainer feature | The `astral-sh` repositories include no devcontainer feature; the container already uses pipx for pre-commit |
| 8 | The migration surface is small | Poetry appears in `Makefile`, the devcontainer (feature, two variables, install line), `.gitignore`, `AGENTS.md`, `CONSTITUTION.md`, `README.md`, three `.claude/settings.json` permissions, `pyproject.toml` (build backend only) and the lock |

Constraints that shape the approach:
- The current `poetry.lock` is tracked and equals what uv resolves today, so switching loses nothing.
- Hooks for ruff and mypy run from pre-commit's isolated environments; that decision from `modernize-toolchain` stands until `migrate-to-ty`.
- The sandbox cannot rebuild the devcontainer, so its changes are verified in pieces.

## Goals / Non-Goals

**Goals:**
- uv is the only package manager: lock, environment, commands, hooks, Dependabot and docs.
- A dependency audit runs when the lock or `pyproject.toml` change, and passes.
- No runtime behavior change.

**Non-Goals:**
- Replacing mypy with ty, which is the next change.
- Changing the build backend or adding a `.python-version` file.
- Adding CI, which has its own roadmap item.
- Touching the `docs` extra, or the `openapi-pydantic` and `textual` bounds.

## Decisions

### uv replaces Poetry, with `pyproject.toml` unchanged
The dependency tables, extras and `dev` group already follow PEP 621 and PEP 735, so uv reads them as they are (finding 1). Only two bounds change, for the audit.

Alternative: stay on Poetry. Rejected: nothing is broken, but the official ty hook, `uv audit` and the audit hook all assume uv, and Dependabot has a first-class `uv` ecosystem. Keeping Poetry would leave two package managers in use for Astral's tools.

### `uv.lock` is tracked and `poetry.lock` is removed
Same reasoning as the earlier decision to track the lock: reproducible environments, a base for CI, and lock updates by Dependabot. Both locks resolve identically today (finding 1), so there is no version churn at the switch.

### The build backend stays `poetry-core`
uv builds with any PEP 517 backend, so the `[build-system]` table is not touched. Moving to `uv_build` is optional and unrelated to the package manager.

### Pre-commit runs through `uv run`
`PRE_COMMIT` becomes `uv run pre-commit`, so the hooks use the lock-pinned pre-commit. The ruff and mypy hooks keep their isolated environments.

### `uv-lock` and `uv-audit` hooks from `uv-pre-commit`, pinned
Both come from `astral-sh/uv-pre-commit` at the tag matching the uv version, `0.13.5`, and run only when `uv.lock` or `pyproject.toml` change, so ordinary commits stay offline (finding 5). `uv-lock` keeps the lock in sync. `uv-audit` passes `--preview-features audit-command`, which acknowledges the command is experimental and silences its warning, and audits every group including `dev`, because dev tools are part of the supply chain.

Alternatives: `uv audit --no-dev`, rejected for that reason; leaving auditing to CI later, rejected because the hook gives feedback before a lock change is committed.

### Widen the pytest bounds instead of ignoring the advisory
`pytest >=9.0.3,<10.0.0` and `pytest-cov >=7.0.0,<8.0.0`; `pytest-mock` is unchanged. The fix exists and the suite passes on it (finding 4).

Alternatives: `--ignore PYSEC-2026-1845`, rejected because a fix is available and ignoring needs your explicit approval; `--ignore-until-fixed`, which does not apply once a fix exists.

### Existing hooks are adjusted for the lock
`uv.lock` is 518 KB, over the 500 KB default of `check-added-large-files`, so that hook excludes `uv.lock` only; the limit stays for every other file. This exclusion was approved explicitly. The ruff hooks listed `toml` among their file types, which hands every TOML file to a Python parser; `poetry.lock` passed only because its syntax happens to be valid Python, while `uv.lock` is not. `toml` is dropped from their `types_or`, so ruff keeps covering all Python, stub and notebook files.

Alternative for the size check: raise the limit with `--maxkb=1024`, rejected because it loosens the check for every file and needs another bump as the lock grows.

### Commands keep their meaning
`make install` runs `uv sync`, which installs the core dependencies and the `dev` group, as `poetry install` did. Extras come from `uv sync --all-extras`. `make update` runs `uv lock --upgrade` then `uv sync`. `uv sync` is exact, so it removes packages outside the selected groups and extras, as Poetry's update did.

### Devcontainer: pipx installs uv
Remove the Poetry feature and `POETRY_*` variables and the Poetry entry from `devcontainer-lock.json`. `post-create.sh` runs `pipx install uv==0.13.5`, `uv sync --all-extras` and `uv run pre-commit install` for both hook types, keeping the ownership and npm lines. The environment stays in `.venv`, which is where VS Code already points.

Alternatives: a community devcontainer feature, rejected because I could not verify one; piping the installer script from the network, rejected as less reproducible than a pinned pipx install.

### Dependabot moves to the `uv` ecosystem
`pip` becomes `uv` with the same weekly schedule, pull request limit and grouping, alongside the existing `pre-commit` and `devcontainers` entries.

## Risks / Trade-offs

- [`uv audit` is experimental and may change] -> The hook revision is pinned and moves only through a reviewed Dependabot pre-commit pull request.
- [The audit needs the network when `uv.lock` or `pyproject.toml` change] -> Ordinary commits do not trigger it; a lock change made offline fails the hook and is retried online.
- [A new advisory can fail the hook on an unrelated lock change] -> Treated as signal. Ignoring an advisory needs your approval each time.
- [A lock-sized exclusion could hide a different oversized `uv.lock`] -> The exclusion is by exact path, and the lock is reviewed in every pull request that changes it.
- [Existing clones hold a Poetry `.venv`] -> Documented in the pull request: `rm -rf .venv && uv sync`, and uv must be installed locally.
- [The `uv.lock` format can change across uv versions] -> uv is pinned in the hook revision and in the devcontainer install.
- [The devcontainer cannot be rebuilt in this sandbox] -> The JSON files are validated, the script is syntax-checked, and its uv commands run in a scratch clone; a rebuild on your machine is the remaining check.
- [pytest 9 and pytest-cov 7 change dev behavior] -> The suite passed on both in the trial, and is re-run after the bounds change.

## Migration Plan

Land as separate commits in dependency order so each can be reverted alone: lock, bounds, commands and hooks, devcontainer, Dependabot. `poetry.lock` stays until the commands no longer use Poetry, and remains recoverable from git history afterwards. Rollback: revert the commits.
