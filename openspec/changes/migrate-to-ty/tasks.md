# Tasks

## 1. Add ty to the dev group

- [x] 1.1 In the `dev` group of `pyproject.toml`, add `ty==0.0.95`, keeping `mypy` for now, and run `uv lock` and `uv sync --all-extras`. Verify `uv run ty --version` prints 0.0.95, `uv lock --check` passes, `uv audit --preview-features audit-command` exits 0, and `uv run pytest tests` reports 97 passed.

## 2. ty configuration and suppressions

- [x] 2.1 In `pyproject.toml`, add a `[[tool.ty.overrides]]` entry scoped to `config_wizard/schema.py` that sets `invalid-mutable-override` and `invalid-attribute-override` to `ignore`, and set `unused-ignore-comment` to `error` under `[tool.ty.rules]`. Verify `uv run --all-extras ty check config_wizard scripts tests` reports 17 diagnostics, none of them in `config_wizard/schema.py`.
- [x] 2.2 Remove the 7 mypy-coded `# type: ignore[assignment]` comments in `config_wizard/schema.py`, which the override now covers, and replace the 6 in `config_wizard/backends/streamlit.py` and `tests/test_schema.py` with 7 `# ty: ignore[rule]` comments placed on the lines ty reports (`invalid-assignment` on lines 485 and 603 and in the test, `not-subscriptable` on 486 and 769, `unresolved-attribute` on 685 and 765). Verify `grep -rn "type: ignore" config_wizard tests` prints nothing and `ty check` shows exactly 10 diagnostics left, none of those three rules.
- [x] 2.3 Add inline `# ty: ignore[rule]` comments for the remaining 10 diagnostics, on 9 lines in `config_wizard/backends/streamlit.py`: `invalid-parameter-default` on line 106, `no-matching-overload` on lines 205, 222, 224, 237, 241, 307 and 796, and `invalid-argument-type` with `unknown-argument` on line 265. Verify `uv run --all-extras ty check config_wizard scripts tests` reports no diagnostics, `grep -rn "ty: ignore" config_wizard tests | wc -l` is 16, `unused-ignore-comment` reports nothing, `make format` passes, and `uv run pytest tests` reports 97 passed. `make lint` is verified in 3.1, because the mypy hook cannot pass once its coded ignores are gone.

## 3. Hook, Makefile and mypy removal

- [x] 3.1 In `.pre-commit-config.yaml`, add a local hook `ty` running `uv run --all-extras ty check` with `pass_filenames: false` and Python file types, set `[tool.ty.src]` to include `config_wizard`, `scripts` and `tests`, remove the `mirrors-mypy` repository, point `make lint` at the `ruff-check` and `ty` hook ids, and remove `[tool.mypy]` and `mypy` from `pyproject.toml`, then run `uv lock`. Verify `make lint` and `make format` exit 0, `uv run pre-commit run ty --all-files` passes from a default `uv sync` environment even with the untracked `test_wizard.py` present, `grep -rn -i mypy pyproject.toml .pre-commit-config.yaml Makefile` prints nothing, and `uv lock --check` passes.
- [x] 3.2 Prove the gate in a scratch copy: introduce an obviously wrong-typed assignment in `config_wizard/utils.py` and run `uv run pre-commit run ty --all-files`. Verify the hook exits non-zero and names the error.

## 4. Documents and devcontainer

- [x] 4.1 Update `AGENTS.md` (the stack paragraph names ty and says the `ty` hook installs the extras, and the `make lint` line), `CONSTITUTION.md` (the development tools line, and the types convention: checked by ty, suppressions are `# ty: ignore[rule]` naming the rule, and `config_wizard/schema.py` has one scoped override for `invalid-mutable-override` and `invalid-attribute-override` because `ResolvedSchema` narrows inherited fields), and `.claude/settings.json` (`uv run ty*` in place of `uv run mypy*`). Verify `grep -n -i mypy AGENTS.md CONSTITUTION.md .claude/settings.json` prints nothing and the JSON parses.
- [x] 4.2 In `.devcontainer/devcontainer.json`, replace `ms-python.mypy-type-checker` with `astral-sh.ty`. Verify the file parses as JSON, `astral-sh.ty` is listed, and `grep -n -i mypy .devcontainer/*` prints nothing. The extension itself can only be confirmed on a container rebuild, which is recorded as the remaining check.

## 5. Dependabot

- [x] 5.1 In `.github/dependabot.yml`, add a group named `ty` with `patterns: ["ty"]` to the `uv` ecosystem, listed before `python-minor-and-patch`. Verify `pre-commit run check-yaml --files .github/dependabot.yml` passes and the `ty` group comes first.

## 6. Integration checks

- [ ] 6.1 In `ROADMAP.md`, delete the `migrate-to-ty` item, renumber the rest, and change the `add-ci-pipeline` item to say `ty` instead of `mypy`. Verify the numbering is consecutive from 1, `grep -n -i mypy ROADMAP.md` prints nothing, and `add-ci-pipeline` is first.
- [ ] 6.2 Run `openspec validate migrate-to-ty --strict`. Verify it reports the change as valid.
- [ ] 6.3 Clone the branch into a new empty directory under the session scratchpad and run `make install`, `make test`, `make lint`, `make format` and `uv build`. Verify pytest reports 97 passed, lint and format pass from the default sync environment (the hook installs the extras itself), and the build succeeds without warnings.
- [ ] 6.4 Run `git diff --name-status origin/main..HEAD` and verify the only changes are `pyproject.toml`, `uv.lock`, `.pre-commit-config.yaml`, `Makefile`, `.github/dependabot.yml`, `AGENTS.md`, `CONSTITUTION.md`, `ROADMAP.md`, `.claude/settings.json`, `.devcontainer/devcontainer.json`, `config_wizard/schema.py`, `config_wizard/backends/streamlit.py`, `tests/test_schema.py` and the change directory.

## Workflow follow-up

- Archive the change with `/opsx:archive`. With `skip_specs: true` there is nothing to sync into `openspec/specs/`.
- If ty cannot reach zero diagnostics with the suppression forms above, stop and switch to the pyrefly fallback described in `design.md` before continuing.
- `add-ci-pipeline` is next. It can use `setup-uv`, run `make lint`, and add the `github-actions` ecosystem to the Dependabot configuration.
