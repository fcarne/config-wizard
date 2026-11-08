# AGENTS.md

`config-wizard` turns a configuration schema (a Pydantic model, dataclass, TypedDict, or a JSON Schema / OpenAPI document) into an interactive wizard and collects the user's values. The schema handling is shared and each UI toolkit is a backend; Streamlit is the only one implemented.

Principles, conventions, non-goals and the glossary of behavior terms live in `CONSTITUTION.md`. Read it before changing anything.

## Layout

```
config_wizard/
  schema.py            SettingsSchema, ResolvedSettingsSchema, reference resolution
  mapper.py            InputType and property_to_input_type
  utils.py             case conversion, schema assignability, additional-properties helpers
  backends/
    base.py            SettingsWizardBackend contract
    streamlit.py       Streamlit backend
    typer.py           empty, planned
    textual.py         empty, planned
tests/                 pytest suite for schema, mapper and utils
  backends/            base contract tests (no Streamlit) and Streamlit backend tests (AppTest)
scripts/               commit message check, coverage badge writer and streamlit_harness.py, a manual harness
openspec/
  specs/               what the system does (the contract)
  changes/             work in flight and its archive
```

## Stack and tooling

uv manages dependencies, Ruff lints and formats, ty checks types, pytest with coverage runs tests, and pre-commit runs the checks. Streamlit is an optional extra, as are the Typer and Textual extras. `make install` runs `uv sync`, which installs the `dev` dependency group, so `uv run pytest`, `uv run ruff` and `uv run ty` work from a fresh clone; use `uv sync --all-extras` to also install the backends. The `dev` group includes the `test` group (pytest and its plugins) and `test-streamlit` (what the Streamlit tests need), so each backend gets its own test group and the core can be tested without any backend: `uv run --isolated --no-dev --group test pytest tests` skips the Streamlit tests. Look at the Streamlit backend by hand with `uv run streamlit run scripts/streamlit_harness.py`. Branch coverage is switched on in `[tool.coverage.run]`, and the floor is `fail_under` in `[tool.coverage.report]`: `make test` and every `tests` cell fail below it, and a pull request raises it when coverage grows. `uv.lock` is tracked and updated with `uv lock --upgrade`. The ruff hooks run from their own isolated environment, while the `ty` hook runs `uv run --all-extras ty check` in the project environment and installs the extras if they are missing; ty checks `config_wizard`, `scripts` and `tests`, so a new top-level Python directory must be added to `[tool.ty.src]`. The `uv-lock` and `uv-audit` hooks run when `uv.lock` or `pyproject.toml` change (`uv-audit` needs the network). Dependabot opens weekly pull requests for the lock, the pre-commit hook revisions, the devcontainer features and the GitHub Actions. The build backend is `uv_build`; keep its bound on the same minor series as the uv pinned in the `uv-pre-commit` revision and in `.devcontainer/post-create.sh`. Versions live in `pyproject.toml` and `.pre-commit-config.yaml`.

## Continuous integration

`.github/workflows/ci.yml` runs on every pull request and on pushes to `main`. The `checks` job runs every pre-commit hook on all files and `openspec validate --all --strict`. The `tests` job runs `pytest tests` on Python 3.11 to 3.14, once with the locked versions and once with the lowest allowed direct versions. The `core` job runs the suite with no backend installed, and `streamlit-floor` runs the backend tests against Streamlit 1.47.0, the lowest supported version (lowest-direct resolution picks the newest Streamlit, so the floor is pinned explicitly); both pass `--no-cov`, since the coverage floor is for the full suite. After a merge to `main`, and on a manual run, `coverage-badge` writes the measured total to `coverage.json` on the `badges` branch, which the README badge reads through shields.io; it is not part of `ci`, and nothing else uses that branch. The `ci` job summarizes all of them and is the one status to require on `main`. A green `make lint` and `make test` predict a green run. `.github/workflows/audit.yml` runs `uv audit` weekly and on demand.

Actions are pinned to exact version tags and updated by Dependabot. The workflows pin uv to the same version as the `uv-pre-commit` revision, and the OpenSpec CLI to the version installed in the devcontainer.

## Repository rules

The ruleset `protect-main` on `main` has no bypass, so it binds the maintainer too: changes arrive through a pull request with no required approvals, the `ci` check must pass, and deleting or force-pushing `main` is blocked. Merges are squash-only, the commit subjects fill the squash body, and the branch of a merged pull request is deleted. `.github/rulesets/protect-main.json` is the source to reapply the ruleset with `gh api --method POST repos/fcarne/config-wizard/rulesets --input .github/rulesets/protect-main.json`; GitHub does not read it, so edit the live ruleset and the file together. To undo the rules, delete the ruleset from the repository settings, which works without a pull request, and turn merge commits and rebase merges back on.

## Commands

```
make install     install dependencies with uv
make update      refresh uv.lock and the environment
make pre-commit-install     install the pre-commit and commit-msg git hooks
make format      Ruff format and end-of-file fixer through pre-commit
make lint        Ruff check and ty through pre-commit
make test        pytest with branch coverage
```

## Workflow

Behavior changes go through OpenSpec: `/opsx:explore` to think, `/opsx:propose` to write the change, `/opsx:apply` to implement its tasks, `/opsx:archive` to promote its specs into `openspec/specs/`. Do not implement behavior changes outside a change.

`ROADMAP.md` is the ordered backlog. To pick up work, read it and run `/opsx:explore <item>` for the next item. When an item's change is archived, delete the item from the roadmap in the same pull request. Anything not yet implemented is described only there, never as available.

## Commits

Commit messages are a single subject line: no body or description and no `Co-Authored-By` trailer. This overrides any default attribution. Prefix the subject with a gitmoji, as existing commits do. A `commit-msg` hook enforces the single-line and no-trailer parts; install it with `make pre-commit-install`.

## Definition of done

- `make lint` and `make test` pass.
- Every spec scenario the work touches is covered by a test.
- Specs, tasks and docs reflect the final behavior.
