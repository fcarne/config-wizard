# Tasks

## 1. Python floor

- [x] 1.1 In `pyproject.toml`, set `requires-python = ">=3.11,<4.0"` and remove the `Programming Language :: Python :: 3.10` classifier, then run `poetry lock` to refresh the lock metadata without moving versions. Verify `poetry check --lock` passes and `grep -n "3\.10" pyproject.toml` prints nothing.
- [x] 1.2 Change the Python line in `CONSTITUTION.md` and the Python line in the `context:` of `openspec/config.yaml` to 3.11, leaving the pyupgrade clause for group 5. Verify `grep -n "3\.10" CONSTITUTION.md openspec/config.yaml` prints nothing and `openspec validate --all --strict` passes.

## 2. Development dependency group and pytest settings

- [x] 2.1 In `pyproject.toml`, add `[dependency-groups]` with a `dev` group holding pytest, pytest-cov and pytest-mock at their current bounds, plus `pre-commit >=4.7,<5`, `ruff >=0.17,<0.18` and `mypy >=2.4,<3`, and remove `dev` from `[project.optional-dependencies]`. Run `poetry lock`. Verify `poetry check --lock` passes and `poetry install --dry-run 2>&1 | grep -ciE "pytest|ruff|mypy|pre-commit"` is above zero.
- [x] 2.2 Rename `[tool.pytest.ini]` to `[tool.pytest.ini_options]`. Verify `poetry run pytest tests -q` now prints the coverage table and writes `htmlcov/`, and still reports 98 passed.
- [x] 2.3 Run `poetry install` and verify `poetry run ruff --version`, `poetry run pre-commit --version` and `poetry run mypy --version` all succeed, and that `poetry run mypy config_wizard` loads the Pydantic plugin. Any type errors it reports under Streamlit's real types are listed for `migrate-to-ty`, not fixed here.
- [x] 2.4 Update `CONSTITUTION.md` (the dependencies section no longer lists `dev` as an extra and names the dependency group) and the stack paragraph in `AGENTS.md` (`make install` installs the group). Verify `grep -n "dev" CONSTITUTION.md AGENTS.md` shows only the new wording and `.claude/settings.json` permissions for `poetry run ruff*` and `poetry run mypy*` now point at working commands.

## 3. Tracked lock and refresh

- [ ] 3.1 Remove `poetry.lock` from `.gitignore`, keeping `poetry.toml` ignored, and add the current lock as a baseline commit, then note in the tooling paragraph of `AGENTS.md` that the lock is tracked and updated with `poetry update`. Verify `git check-ignore poetry.lock` prints nothing, `git ls-files poetry.lock` lists it and `poetry check --lock` passes.
- [ ] 3.2 Run `poetry update` as its own change after the baseline. Verify `poetry check --lock` passes, `poetry show pydantic` reports a version above 2.11.7, `git diff pyproject.toml` is empty (no bound changed) and `git diff --stat poetry.lock` shows the refresh separate from the baseline.
- [ ] 3.3 Run `poetry install --all-extras` and `make test`. Verify 98 tests pass. If a schema test fails, record whether Pydantic's generated JSON Schema changed semantically and stop for a decision before touching any expectation.
- [ ] 3.4 Run the README example under Streamlit's `AppTest` with the refreshed Streamlit. Verify it reports no exceptions and returns `{"host": "127.0.0.1", "port": 8000, "debug": false}`.

## 4. Hook bumps

- [ ] 4.1 In `.pre-commit-config.yaml`, set `pre-commit-hooks` to `v6.0.0`, `ruff-pre-commit` to `v0.17.2` and `mirrors-mypy` to `v2.4.0`, leaving pyupgrade for group 5. Verify `make lint` and `make format` exit 0, or list each new finding.
- [ ] 4.2 Fix any new ruff or mypy findings with equivalent changes, with no suppressions, and record the size of any reformatting diff. Verify `make lint` exits 0 and `make test` reports 98 passed. Stop for a decision if a fix would change behavior.

## 5. Ruff rules

- [ ] 5.1 In `pyproject.toml`, add `[tool.ruff.lint]` selecting `E4, E7, E9, F, I, UP, B, SIM, PT` (the existing defaults plus the new rules) and re-run `ruff check --statistics` with the bumped version. Verify the per-rule counts are recorded, since 0.12.5 reported 22.
- [ ] 5.2 Apply the import-order autofixes. Verify `ruff check --select I` reports nothing and `make test` reports 98 passed.
- [ ] 5.3 Fix the pytest findings in `tests/`: use tuples for `parametrize` names and remove the second `(Schema(type=DataType.NULL), InputType.NULL)` case in `tests/test_mapper.py`. Verify `ruff check tests --select PT` reports nothing and `make test` reports 97 passed.
- [ ] 5.4 Fix the remaining `SIM` and `UP` findings in `config_wizard/` with equivalent rewrites, keeping `_is_clear_button_disabled` behaving exactly as before. Verify `make lint` exits 0, `make test` reports 97 passed, and the README example under `AppTest` returns the same dictionary as in 3.3.
- [ ] 5.5 Remove the pyupgrade hook from `.pre-commit-config.yaml` and change the pyupgrade clause in `CONSTITUTION.md` to say Ruff's `UP` rules keep code current. Verify `grep -rn "pyupgrade" . --include=*.yaml --include=*.md --exclude-dir=openspec --exclude-dir=.venv` prints nothing and `make lint` exits 0.

## 6. Dependabot

- [ ] 6.1 Add `.github/dependabot.yml` with the `pip`, `pre-commit` and `devcontainers` ecosystems on a weekly schedule, a small `open-pull-requests-limit`, and grouped minor and patch updates, and mention it in the tooling paragraph of `AGENTS.md`. Verify `pre-commit run check-yaml --files .github/dependabot.yml` passes and each `package-ecosystem` value appears in GitHub's supported ecosystems list.

## 7. Integration checks

- [ ] 7.1 Delete item 1 from `ROADMAP.md` and renumber the rest. Verify the numbering is consecutive from 1 and the `migrate-to-ty` item is now first.
- [ ] 7.2 Run `openspec validate modernize-toolchain --strict`. Verify it reports the change as valid.
- [ ] 7.3 Clone the branch into a new empty directory under the session scratchpad and run `make install` followed by `make test` there. Verify pytest runs and reports 97 passed, which confirms a fresh clone is a working development environment.
- [ ] 7.4 Run `git status` and verify the only changes are `pyproject.toml`, `poetry.lock`, `.gitignore`, `.pre-commit-config.yaml`, `.github/dependabot.yml`, `CONSTITUTION.md`, `AGENTS.md`, `ROADMAP.md`, `openspec/config.yaml`, the change directory, and the source and test edits from group 5.

## Workflow follow-up

- Archive the change with `/opsx:archive`. With `skip_specs: true` there is nothing to sync into `openspec/specs/`.
- Start `migrate-to-ty` next. `add-ci-pipeline` adds the `github-actions` ecosystem to the Dependabot configuration when workflows exist.
