# Design

## Context

See `proposal.md` for motivation. Evidence from scratch runs and read-only queries on `main` at `0fdad84`; the repository was not touched.

| # | Finding | Evidence |
|---|---------|----------|
| 1 | The measured coverage | 85.31% on Python 3.11, 3.12 and 3.13 (601 statements, 250 branches, 71 missed, 42 partial) and 84.92% on 3.14, which counts 579 statements. The core modules (`schema.py`, `mapper.py`, `utils.py`, `base.py`) are at 100%; `streamlit.py` is at 77% |
| 2 | Coverage differs by job shape | `tests` (full suite) 85.31%; `streamlit-floor` (`pytest tests/backends`) 80.85%; `core` (no Streamlit) 35%, with `streamlit.py` at 0% |
| 3 | A `fail_under` in the coverage config gates pytest runs | In a scratch copy with `fail_under = 99`, `pytest tests` printed "FAIL Required test coverage of 99.0% not reached. Total coverage: 84.92%" and exited 1; with `--no-cov` the same config exited 0; with `fail_under = 84` it printed "Required test coverage of 84.0% reached" and exited 0 |
| 4 | `coverage json` has what the badge needs | `totals.percent_covered` (84.92159...) and `totals.percent_covered_display` ("85") |
| 5 | Shields can read a JSON file | The endpoint badge takes the file's URL in `url` and needs `schemaVersion` (always 1), `label` and `message`; `color` is optional; `cacheSeconds` has a minimum of 300 ([shields.io endpoint badge documentation](https://shields.io/badges/endpoint-badge)) |
| 6 | The branch to write to is not protected | The `protect-main` ruleset includes only `refs/heads/main`; a push to `badges` is not covered |
| 7 | No secret is needed | `gh secret list` and `gh variable list` are empty; the workflow default token permission is `read`, and `ci.yml` declares `contents: read` at the top. A job can declare more for itself |
| 8 | A push with the default token starts no workflow | GitHub documents that events caused by `GITHUB_TOKEN` do not create new workflow runs, so updating `badges` cannot loop ([GitHub, automatic token authentication](https://docs.github.com/pt/enterprise-server@3.4/actions/security-guides/automatic-token-authentication)) |
| 9 | Pushes to `main` run the workflow one at a time per ref | `ci.yml` has a per-ref concurrency group that cancels in-progress runs only for pull requests |
| 10 | The README badge today | `https://img.shields.io/badge/coverage-85%25-yellowgreen`, edited by hand in the last pull request |

Constraints that shape the approach:
- The ruleset has no bypass, so nothing can commit to `main` from CI; the badge cannot live on `main`.
- The project rules forbid explanatory comments, and new tooling should be small enough to read in one pass.
- `core` and `streamlit-floor` run for reasons other than coverage and must not inherit the floor.

## Goals / Non-Goals

**Goals:**
- A pull request that drops total coverage below the floor fails CI, and the same check fails locally in `make test`.
- The README badge shows the coverage measured on `main` without anyone editing the README.
- No new secret and no third-party service.

**Non-Goals:**
- An automatic ratchet, a second gate on the core modules, patch coverage, pull request comments, per-file floors, and gating the `core` and `streamlit-floor` jobs.

## Decisions

### The floor lives in `[tool.coverage.report]`, set to 84
`fail_under = 84` is the one place the number is written, next to the other coverage settings, as branch coverage now is (`[tool.coverage.run]`). It applies to `make test`, to every `tests` cell and to a local `pytest tests`. 84 is below the lowest measurement (84.92% on 3.14) and 1.31 points below the 3.11 to 3.13 value; raising it is an ordinary pull request that edits this number.

Alternatives: pass `--cov-fail-under` on the command line in one CI cell (rejected: local runs would not enforce it and the number would sit in the workflow); a floor of 85 gated on one cell only (rejected: it would leave 3.14 unchecked and be higher than what every version measures).

### `core` and `streamlit-floor` run with `--no-cov`
Both jobs exist to test something else (the core without a backend, the backend on the lowest Streamlit) and measure 35% and 80.85%. They pass `--no-cov`, which pytest-cov honors even with the floor configured (finding 3), so the floor stays global and the exceptions are visible in the workflow.

Alternative: overriding the floor to 0 in those jobs with `--cov-fail-under=0` (rejected: it keeps measuring and printing a coverage table that means nothing for them).

### The badge is an endpoint file on a `badges` branch
A job `coverage-badge` runs after `tests` on pushes to `main` and on manual runs on `main` (`github.event_name != 'pull_request'` and the ref is `main`), with `permissions: contents: write` on that job only. It runs the suite on Python 3.12, runs `coverage json`, turns the total into `{"schemaVersion": 1, "label": "coverage", "message": "85%", "color": ...}` with `scripts/coverage_badge.py`, and force-pushes it as the only commit of an orphan branch `badges` (a single file, `coverage.json`). The README badge is `https://img.shields.io/endpoint?url=<raw.githubusercontent.com URL of badges/coverage.json>`, which never changes.

The job is not part of the `ci` job's `needs`: it only runs on `main` after a merge, so a failure to publish cannot block anything, and `ci` stays the one required status. It needs `tests` to have succeeded, so a red `main` does not publish a number.

Why force-push one orphan commit: no history to grow, no fetch or merge logic, and nothing else writes to the branch. Why rerun the suite instead of passing the number from a `tests` cell: it keeps the job independent of the matrix and costs about ten seconds.

Alternatives: Codecov or Coveralls (rejected: a third-party app and a secret, with features this project does not need yet); a gist updated by a community action (rejected: needs a gist-scope token secret); committing an SVG to `main` (impossible under `protect-main`); typing the badge by hand (the current problem).

### The color follows fixed thresholds
`scripts/coverage_badge.py` reads coverage.py's JSON and writes the endpoint file: message the rounded percentage with `%`, color `brightgreen` from 90, `yellowgreen` from 80, `yellow` from 70, otherwise `red`, chosen from the rounded number that is shown so the color never disagrees with it (89.6 shows as 90% and is `brightgreen`). 85 therefore stays `yellowgreen`, as today. The script is a pure function plus a small command line entry, in `scripts/` so `ruff` and `ty` check it.

### Raising the floor is manual
When coverage grows, a pull request raises `fail_under`. A ratchet that raises it automatically would need state; the `badges` file could hold it, but that couples the gate to a publishing job and is left out.

## Risks / Trade-offs

- [Job-level `contents: write` may not work while the repository default is read-only] → The job declares the permission itself, which overrides the default; this is verified by a manual run on `main` after the merge, and if it fails the fix is the repository's Actions setting or a pull request.
- [The badge cannot be tested before the merge] → The job only runs on `main`, and the README badge shows a broken image until the first run. The script is verified locally with sample input, the workflow with actionlint, and the whole path by a manual run right after the merge (the last tasks).
- [Shields and the raw file are cached, so the badge lags by minutes] → Accepted; the minimum cache is five minutes and the number only changes on merges.
- [A statement-count difference between Python versions moves the percentage] → The floor sits below the lowest measured value (3.14); a version-specific shift larger than about 0.9 points would fail that cell and be a real signal.
- [Force-pushing `badges` rewrites it] → Nothing else uses the branch; if it is deleted the next run recreates it.
- [The floor blocks a pull request that adds code with a defensive branch that is hard to test] → The pull request adds a test or raises the question; lowering the floor is a visible change to one line.

## Migration Plan

1. Merge the pull request with the floor, the `--no-cov` flags, the script, the job and the README badge URL. The README badge is broken until step 2.
2. Run the workflow manually on `main` (`gh workflow run ci.yml --ref main`) and check that `badges` exists, `coverage.json` has the expected content, and the shields URL renders `coverage 85%`.
3. Archive the change.

Rollback: revert the pull request, and delete the `badges` branch if it was created. The README badge can be put back to a static one in the same revert.
