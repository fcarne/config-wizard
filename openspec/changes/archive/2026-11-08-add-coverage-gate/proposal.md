# Proposal

## Why

The backends now have tests, so coverage is 85% with branches, but nothing keeps it there: a pull request can delete tests or add untested code and CI stays green. The README badge is also typed by hand (`coverage-85%25-yellowgreen`), and it went from 31% to 85% only because a pull request edited it, so it will drift the next time the suite changes. Both items were waiting on the Streamlit tests, which are merged.

## What Changes

- Add a coverage floor of 84% (total, with branches) as `fail_under` in `[tool.coverage.report]`. It applies to every pytest run that measures coverage, including `make test`, so the same check runs locally and in CI. The floor is 84, not 85, because the suite measures 85.31% on Python 3.11 to 3.13 and 84.92% on 3.14, which counts fewer statements.
- Run the `core` and `streamlit-floor` jobs with `--no-cov`. They test other things on purpose (the core with no backend installed measures 35%, the backend tests alone 80.85%), so the floor does not apply to them.
- Generate the README badge instead of typing it: after every merge to `main` (and on a manual run), a new job writes the measured percentage to `coverage.json` on a `badges` branch in the format of a shields.io endpoint badge, and the README badge points at that file, so the README is never edited for coverage again. The job needs no secret and no third-party service, runs only on `main`, and holds `contents: write` for that job only.
- Add `scripts/coverage_badge.py`, the small script that turns coverage.py's JSON into the endpoint file (message `85%`, colored by threshold).
- Update the README (badge URL and status sentence), `AGENTS.md` (the gate, the badge job, how to raise the floor) and the roadmap (delete this item).
- Runtime behavior is unchanged. This is tooling and documentation, so the change sets `skip_specs: true`.

## Capabilities

### New Capabilities

None. This change is CI and configuration only.

### Modified Capabilities

None. No requirement in `openspec/specs/` mentions coverage.

## Impact

- New file: `scripts/coverage_badge.py`.
- Changed files: `pyproject.toml` (the floor), `.github/workflows/ci.yml` (`--no-cov` on two jobs and the badge job), `README.md`, `AGENTS.md`, `ROADMAP.md`.
- A new `badges` branch is created in the repository by the first run of the badge job, outside the pull request. It holds one file, `coverage.json`, and is rewritten as a single commit on every update.
- Out of scope: an automatic ratchet that raises the floor by itself, a second gate that pins the core modules at 100%, patch (diff) coverage and pull request comments, which would come from a service such as Codecov and need a secret.
