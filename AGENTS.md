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
openspec/
  specs/               what the system does (the contract)
  changes/             work in flight and its archive
```

## Stack and tooling

uv manages dependencies, Ruff lints and formats, ty checks types, pytest with coverage runs tests, and pre-commit runs the checks. Streamlit is an optional extra, as are the Typer and Textual extras. `make install` runs `uv sync`, which installs the `dev` dependency group, so `uv run pytest`, `uv run ruff` and `uv run ty` work from a fresh clone; use `uv sync --all-extras` to also install the backends. `uv.lock` is tracked and updated with `uv lock --upgrade`. The ruff hooks run from their own isolated environment, while the `ty` hook runs `uv run --all-extras ty check` in the project environment and installs the extras if they are missing; ty checks `config_wizard`, `scripts` and `tests`, so a new top-level Python directory must be added to `[tool.ty.src]`. The `uv-lock` and `uv-audit` hooks run when `uv.lock` or `pyproject.toml` change (`uv-audit` needs the network). Dependabot opens weekly pull requests for the lock, the pre-commit hook revisions and the devcontainer features. The build backend is `uv_build`; keep its bound on the same minor series as the uv pinned in the `uv-pre-commit` revision and in `.devcontainer/post-create.sh`. Versions live in `pyproject.toml` and `.pre-commit-config.yaml`.

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
