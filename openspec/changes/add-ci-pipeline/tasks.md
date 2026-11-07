# Tasks

## 1. Fix the Python 3.11 test failure

- [ ] 1.1 In `tests/conftest.py`, import `TypedDict` from `typing_extensions` and keep `Any` from `typing`. Verify `uv run --python 3.11 pytest tests` and `uv run --python 3.12 pytest tests` both report 97 passed, and `make lint` and `make format` pass.

## 2. The CI workflow

- [ ] 2.1 Create `.github/workflows/ci.yml` as designed: triggers `pull_request`, `push` to `main` and `workflow_dispatch`; `permissions: contents: read`; a concurrency group that cancels superseded pull request runs; a timeout on every job; a `checks` job (checkout, setup-uv at 0.13.6 with caching, `uv sync --all-extras`, the pre-commit environment cache, `uv run pre-commit run --all-files`, setup-node 22, and `npx --yes @fission-ai/openspec@1.15.0 validate --all --strict`); a `tests` job matrixed over Python 3.11, 3.12, 3.13 and 3.14 by highest and lowest-direct resolution, each cell ending with a step that fails if a tracked file changed; and a `ci` job that needs both, always runs, and fails unless both succeeded. Use the exact action tags from the design. Verify `uvx --from actionlint-py actionlint .github/workflows/ci.yml` reports nothing and `uv run pre-commit run check-yaml --files .github/workflows/ci.yml` passes.
- [ ] 2.2 In a fresh scratch clone, run every command the workflow runs: for `checks`, `uv sync --all-extras`, `uv run pre-commit run --all-files` and the pinned `npx` validation; for `tests`, the highest command (`uv run --python <version> pytest`) and the lowest-direct command (`uv run --isolated --resolution lowest-direct --python <version> pytest`) on Python 3.11 and 3.14. Verify every command exits 0, `git status --short` is empty afterwards in each case, and the lowest-direct run leaves `uv.lock` untouched.

## 3. The audit workflow

- [ ] 3.1 Create `.github/workflows/audit.yml` triggered by a weekly `schedule` and by `workflow_dispatch`, with `permissions: contents: read`, a timeout, setup-uv at 0.13.6, and one step running `uv audit --preview-features audit-command`. Verify actionlint and `check-yaml` pass and the audit command exits 0 on the current lock.

## 4. Pull request template and Dependabot

- [ ] 4.1 Create `.github/pull_request_template.md` with a line for the OpenSpec change (or none), a short summary, and a verification checklist covering `make lint`, `make test`, `openspec validate --all --strict`, a test for each touched spec scenario, and removing the roadmap item. Verify the file exists, is under 25 lines, and `uv run pre-commit run --all-files` still passes.
- [ ] 4.2 In `.github/dependabot.yml`, add a `github-actions` ecosystem on a weekly schedule with a pull request limit of 3 and grouped minor and patch updates. Verify `check-yaml` passes, the ecosystems are exactly `uv`, `pre-commit`, `devcontainers` and `github-actions`, and `github-actions` appears in GitHub's supported ecosystems list.

## 5. Metadata, devcontainer and documents

- [ ] 5.1 In `pyproject.toml`, add the `Programming Language :: Python :: 3.14` classifier. Verify `uv lock --check` passes, `uv build` prints no warnings and the wheel metadata lists 3.14, and `uv run --python 3.14 pytest tests` reports 97 passed.
- [ ] 5.2 In `.devcontainer/post-create.sh`, pin uv with `pipx install uv==0.13.6` (it says 0.13.5 while the hook revision is 0.13.6) and install `@fission-ai/openspec@1.15.0` instead of `@latest`, leaving `opencode-ai@latest` unchanged. Verify `bash -n` passes, and `grep -n "uv==\|openspec" .devcontainer/post-create.sh` shows both pins with the uv one matching the `uv-pre-commit` `rev:` in `.pre-commit-config.yaml`.
- [ ] 5.3 In `AGENTS.md`, add a short CI section (what each job runs, that a green `make lint` and `make test` predict a green run, that `ci` is the status to require, and that actions are pinned to exact tags and updated by Dependabot), and add a CI status badge for `ci.yml` to `README.md`. Verify `grep -n "ci.yml" README.md` shows the badge and the new `AGENTS.md` section is present.

## 6. Integration checks

- [ ] 6.1 In `ROADMAP.md`, delete the `add-ci-pipeline` item and renumber the rest; the follow-ups `protect-main-branch`, `add-coverage-gate`, `lint-pull-request-titles`, `add-release-workflow`, `add-documentation-site` and `test-other-platforms` are already on the roadmap. Verify the numbering is consecutive from 1, `protect-main-branch` is first, and those six items are present.
- [ ] 6.2 Run `openspec validate add-ci-pipeline --strict`. Verify it reports the change as valid.
- [ ] 6.3 Clone the branch into a new empty directory under the session scratchpad and run `make install`, `make test`, `make lint`, and actionlint on both workflows. Verify 97 passed, lint passes and actionlint reports nothing.
- [ ] 6.4 Run `git diff --name-status origin/main..HEAD` and verify the only changes are `.github/workflows/ci.yml`, `.github/workflows/audit.yml`, `.github/pull_request_template.md`, `.github/dependabot.yml`, `pyproject.toml`, `tests/conftest.py`, `.devcontainer/post-create.sh`, `AGENTS.md`, `README.md`, `ROADMAP.md` and the change directory.
- [ ] 6.5 Push the branch, open the pull request, and wait for its CI run. Verify `gh pr checks` shows `checks`, all eight `tests` cells and `ci` passing.

## Workflow follow-up

- Archive the change once its CI run is green; the archive commit runs CI again.
- Continue with `protect-main-branch`, which requires `ci` on `main` after the first green run and changes the squash-merge message setting from `COMMIT_MESSAGES` to `BLANK`.
- `add-coverage-gate` follows `test-streamlit-backend`.
