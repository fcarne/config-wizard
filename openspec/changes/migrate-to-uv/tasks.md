# Tasks

## 1. uv lock and parity

- [ ] 1.1 Run `uv lock` to create `uv.lock` with `pyproject.toml` untouched, and add it, leaving `poetry.lock` in place for now. Verify `uv lock --check` passes, `git diff pyproject.toml` is empty, and pydantic, pydantic-core, streamlit, pytest, ruff, mypy, jsonschema, typing-extensions, openapi-pydantic, textual and typer have the same versions in `uv.lock` and `poetry.lock`.
- [ ] 1.2 Recreate the project environment with `uv sync --all-extras` after removing `.venv`, which `poetry install` can rebuild from `poetry.lock` until task 3.3. Verify `uv run pytest tests` reports 97 passed and the README example under Streamlit's `AppTest` returns `{"host": "127.0.0.1", "port": 8000, "debug": false}`.

## 2. Dependency bounds for the audit

- [ ] 2.1 In the `dev` group of `pyproject.toml`, set `pytest >=9.0.3,<10.0.0` and `pytest-cov >=7.0.0,<8.0.0`, then run `uv lock` and `uv sync --all-extras`. Verify `uv audit --preview-features audit-command` exits 0 and reports no vulnerabilities, `uv run pytest tests` reports 97 passed on pytest 9, and `uv lock --check` passes.

## 3. Commands, hooks and documents

- [ ] 3.1 In the `Makefile`, replace the Poetry variables with `UV := uv`, `PYTHON := uv run python` and `PRE_COMMIT := uv run pre-commit`, make `install` run `uv sync` and `update` run `uv lock --upgrade` then `uv sync`, and remove Poetry from the target descriptions. Verify `make install`, `make test` (97 passed), `make format` and `make lint` exit 0, `make pre-commit-install` installs both hook types, and `make help` mentions no Poetry.
- [ ] 3.2 Add the `uv-lock` and `uv-audit` hooks from `https://github.com/astral-sh/uv-pre-commit` at rev `0.13.5` to `.pre-commit-config.yaml`, with `args: [--preview-features, audit-command]` on `uv-audit`. Verify `uv run pre-commit run uv-lock --all-files` and `uv run pre-commit run uv-audit --all-files` pass, and that in a scratch copy with the pytest bound reset to `<9.0.0` the `uv-audit` hook fails.
- [ ] 3.3 Remove `poetry.lock` and the Poetry block from `.gitignore`. Verify `git ls-files poetry.lock` prints nothing, `grep -n -i poetry .gitignore` prints nothing, and `uv lock --check` and `make test` still pass.
- [ ] 3.4 Update `README.md` (install with `uv sync --extra streamlit`, run with `uv run streamlit run app.py`), `AGENTS.md` (uv manages dependencies, `uv.lock` is tracked and updated with `uv lock --upgrade`, the `uv-lock` and `uv-audit` hooks, and `uv sync --all-extras` for the backends), `CONSTITUTION.md` (the development tools line names `uv sync`) and `.claude/settings.json` (`uv run pytest*`, `uv run ruff*`, `uv run mypy*`). Verify `grep -n -i poetry README.md AGENTS.md CONSTITUTION.md .claude/settings.json Makefile .pre-commit-config.yaml` prints nothing, the JSON parses, and the README example still returns the same dictionary under `AppTest` in the uv environment.

## 4. Devcontainer

- [ ] 4.1 In `.devcontainer/devcontainer.json`, remove the Poetry feature and the `POETRY_VIRTUALENVS_IN_PROJECT` and `POETRY_NO_INTERACTION` variables, and remove the Poetry entry from `.devcontainer/devcontainer-lock.json`. Verify both files parse as JSON and neither mentions Poetry.
- [ ] 4.2 In `.devcontainer/post-create.sh`, replace the Poetry and pre-commit lines with `pipx install uv==0.13.5`, `uv sync --all-extras` and `uv run pre-commit install --hook-type pre-commit --hook-type commit-msg`, keeping the ownership and npm lines. Verify `bash -n` passes, `grep -n -i poetry .devcontainer/*` prints nothing, and running the two uv lines in a fresh scratch clone gives a working environment (`uv run pytest tests` reports 97 passed and the `commit-msg` hook is installed). A container rebuild on your machine is the remaining check, and is recorded as such.

## 5. Dependabot

- [ ] 5.1 In `.github/dependabot.yml`, replace the `pip` ecosystem with `uv`, keeping the weekly schedule, pull request limit and grouping. Verify `pre-commit run check-yaml --files .github/dependabot.yml` passes, the ecosystems are exactly `uv`, `pre-commit` and `devcontainers`, and `uv` appears in GitHub's supported ecosystems list.

## 6. Integration checks

- [ ] 6.1 Run `openspec validate migrate-to-uv --strict`. Verify it reports the change as valid.
- [ ] 6.2 Clone the branch into a new empty directory under the session scratchpad and, with the directory containing `poetry` removed from `PATH`, run `make install`, `make test` and `make lint`. Verify pytest reports 97 passed, lint passes, and no step needed Poetry.
- [ ] 6.3 Run `git status` and verify the only changes are `pyproject.toml`, `uv.lock`, the removal of `poetry.lock`, `.gitignore`, `Makefile`, `.pre-commit-config.yaml`, `.claude/settings.json`, `README.md`, `AGENTS.md`, `CONSTITUTION.md`, `.devcontainer/devcontainer.json`, `.devcontainer/devcontainer-lock.json`, `.devcontainer/post-create.sh`, `.github/dependabot.yml` and the change directory.

## Workflow follow-up

- Archive the change with `/opsx:archive`. With `skip_specs: true` there is nothing to sync into `openspec/specs/`.
- Start `migrate-to-ty` next, using the uv environment and the strategy already chosen there (narrow inline suppressions). `add-ci-pipeline` then uses `setup-uv` and adds the `github-actions` ecosystem to the Dependabot configuration.
