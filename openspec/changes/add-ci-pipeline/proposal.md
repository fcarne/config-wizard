# Proposal

## Why

Nothing enforces the project's checks on a pull request. Lint, types, tests, OpenSpec validation and the dependency audit run only through local hooks and one author's discipline (known issue 12). Measuring what a pipeline would see already found real gaps. The suite has failed one test on Python 3.11 since the floor was raised to 3.11, because every local run uses the container's 3.12; Python 3.14 passes but is not claimed; and the declared lower dependency bounds hold, which a matrix can keep true.

## What Changes

- Add a CI workflow that runs on pull requests and on pushes to `main`: a `checks` job (every pre-commit hook on all files, including ruff, ty, `uv-lock` and `uv-audit`, plus `openspec validate --all --strict`), a `tests` matrix (Python 3.11, 3.12, 3.13 and 3.14, each with the newest and the lowest allowed direct dependencies), and an aggregating `ci` job that is the one status to require.
- Add a scheduled and manually triggerable workflow that runs `uv audit` weekly, so a new advisory is noticed even when no pull request is open.
- Fix the Python 3.11 failure: the test fixture builds its TypedDict from `typing_extensions`, which pydantic requires below 3.12.
- Add the Python 3.14 classifier now that CI tests it.
- Add a pull request template that links the OpenSpec change, and a `github-actions` ecosystem to Dependabot.
- Pin third-party actions to exact version tags (no comments, no SHAs) and pin the OpenSpec CLI to 1.15.0 in CI and in the devcontainer, which currently installs `@latest`.
- Update `AGENTS.md` with a CI section, add a CI status badge to `README.md`, and update the roadmap.
- No runtime behavior changes.

## Capabilities

### New Capabilities

None. This change is tooling and tests only, so it sets `skip_specs: true`.

### Modified Capabilities

None. No requirement in `openspec/specs/` mentions CI or supported Python versions.

## Impact

- New files: `.github/workflows/ci.yml`, `.github/workflows/audit.yml`, `.github/pull_request_template.md`.
- Changed files: `.github/dependabot.yml`, `pyproject.toml` (one classifier), `tests/conftest.py`, `.devcontainer/post-create.sh`, `AGENTS.md`, `README.md`, `ROADMAP.md`.
- Out of scope, each now its own roadmap item: `protect-main-branch` (requiring the `ci` check on `main` and changing the repository's squash-merge setting, which adds a body listing every commit and so bypasses the single-line commit rule at merge time), `add-coverage-gate` (which waits for `test-streamlit-backend` because the backends are at 0%), `lint-pull-request-titles`, `add-release-workflow`, `add-documentation-site` and `test-other-platforms`.
