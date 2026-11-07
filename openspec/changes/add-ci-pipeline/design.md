# Design

## Context

See `proposal.md` for motivation. Evidence from scratch clones of `main` (commit `1c260fc`) and read-only GitHub queries; nothing in the repository was touched:

| # | Finding | Evidence |
|---|---------|----------|
| 1 | There is no CI | `.github/` holds only `dependabot.yml`; the 12 workflow runs on record are GitHub's own "Dependabot Updates"; Actions is enabled with all actions allowed, read-only default token permissions and no SHA-pinning requirement; `main` has no protection or rulesets; the repository is public |
| 2 | Python 3.11 fails one test, and the cause is a library bug | `test_from_schema__valid_types__returns_schema[user_typeddict]` fails on 3.11 with pydantic's `typed-dict-version` error because the fixture uses `typing.TypedDict`. Switching the fixture to `typing_extensions.TypedDict`, which pydantic requires below 3.12, then fails on 3.12 too with `TypeError: The schema must be a Pydantic model, TypedDict, or dataclass`: `schema.py` detects TypedDicts with `typing.is_typeddict`, which returns False for a class built from `typing_extensions.TypedDict`, while `typing_extensions.is_typeddict` returns True for both kinds. So a TypedDict could not be loaded at all on 3.11, and on 3.12 and later only the `typing` kind worked; `streamlit.py` already uses `typing_extensions.TypedDict` |
| 3 | 3.12, 3.13 and 3.14 pass | 97 passed on each, in 3 to 12 s |
| 4 | The lower bounds hold | With the lowest allowed direct versions (pydantic 2.11.7, jsonschema 4.25.0, openapi-pydantic 0.5.1, typing-extensions 4.14.1, pytest 9.0.3) all 97 pass on 3.12; on 3.11 only the same TypedDict test fails. Running `uv run --resolution lowest-direct` without `--isolated` rewrote `uv.lock` in the scratch clone |
| 5 | The hook set is CI-sized | `pre-commit run --all-files` passes in 44 s with warm hook environments, and includes `uv-audit`, which needs the network; the `commit-msg` hook is not part of it |
| 6 | OpenSpec validation is cheap | `openspec validate --all --strict` passes in 1 s with CLI 1.15.0, while `post-create.sh` installs `@latest` |
| 7 | Coverage is low and unevenly spread | 31.52% in total; a `--cov-fail-under` of 31 passes and 32 fails; `base.py` and `streamlit.py` are at 0% |
| 8 | The squash setting bypasses the commit rule | The repository squashes with `squash_merge_commit_message: COMMIT_MESSAGES`, so each of the four pull requests merged so far carries a 10 to 19 line body on `main` |
| 9 | The actions are current and tags exist | `astral-sh/setup-uv` v10.3.3, `actions/checkout` v7.0.1, `actions/cache` v6.1.0 and `actions/setup-node` v7.1.0 all exist as exact tags; `setup-uv` takes `version`, `python-version` and `enable-cache`, and by default keys its cache on `uv.lock` |
| 10 | Workflows can be linted locally | `actionlint-py` 1.7.12 wraps the `actionlint` binary |
| 11 | The lowest pydantic cannot run on 3.14 | The lowest-direct resolution picks pydantic 2.11.7, whose pydantic-core 2.33.2 ships no cp314 wheel, so uv tries to build it from source with maturin and fails; the earliest pydantic-core with cp314 wheels is 2.35.0, and pydantic first supports 3.14 in 2.12.0 (pydantic-core 2.41.1). With the requirement split by environment marker, a scratch run resolved 2.11.7 on 3.11 to 3.13 and 2.12.0 on 3.14, all four lowest-direct runs passed, the lock kept a single pydantic entry, and the built metadata kept both `Requires-Dist` lines with their markers |

Constraints that shape the approach:
- Workflows cannot run locally, so they are linted locally and proven by their own run on this change's pull request.
- The project rules forbid explanatory comments, which rules out the common `# vX.Y.Z` annotation beside a commit SHA.
- The hooks pin uv to 0.13.6 (Dependabot bumped the hook revision) while `post-create.sh` still says 0.13.5, and the lock is the only dependency source.

## Goals / Non-Goals

**Goals:**
- Every check the project already defines runs on every pull request and on `main`, and one status summarizes them.
- Each Python version the package claims, and the lowest dependencies it allows, are tested.
- A new advisory is noticed within a week without a pull request.
- No runtime behavior change beyond the TypedDict detection fix.

**Non-Goals:**
- Branch protection, the squash-merge setting, coverage gating, pull request title linting, releases, documentation builds and other operating systems, each now a roadmap item (see `proposal.md`).

## Decisions

### Two workflows, one required status
`ci.yml` runs on `pull_request`, on `push` to `main` and on `workflow_dispatch`, with `permissions: contents: read`, a per-ref concurrency group that cancels superseded pull request runs, and a timeout on every job. It contains three jobs: `checks`, `tests` and `ci`. The `ci` job needs the other two, always runs, and fails unless both succeeded, so branch protection later requires one stable name instead of eight matrix names. `audit.yml` runs on a weekly schedule and on `workflow_dispatch`.

Alternative: one file with a schedule trigger. Rejected: different triggers and a different purpose are clearer apart.

### `checks` runs the project's own hooks
One job on Python 3.12: install uv, `uv sync --all-extras`, restore the pre-commit environment cache, `uv run pre-commit run --all-files`, then `openspec validate --all --strict` through `npx` at 1.15.0. This is the same hook set as locally, so a green local run predicts a green CI run (finding 5). `uv-audit` runs on every pull request and can therefore fail an unrelated pull request when a new advisory appears; that is accepted as a signal, and the scheduled audit surfaces it earlier.

Alternative: skip `uv-audit` in pull requests and rely on the schedule. Rejected: skipping a hook is a bypass, and the audit is the point of tracking the lock.

### `tests` is a version and resolution matrix
Python 3.11, 3.12, 3.13 and 3.14, each with the highest and the lowest-direct resolution, eight cells. Highest runs `uv run --python <version> pytest tests`. Lowest runs `uv run --isolated --resolution lowest-direct --python <version> pytest tests`, where `--isolated` stops it rewriting `uv.lock` (finding 4). Every cell ends by failing if it changed a tracked file. Both name the `tests` directory, as `make test` does, so stray `test_*.py` files elsewhere are never collected. The suite takes seconds, so the matrix costs setup time, not test time.

Alternative: test only 3.12. Rejected: that is how 3.11 broke unnoticed (finding 2).

### The pydantic floor depends on the Python version
`pydantic[email]` is declared twice with environment markers: `>=2.11.7,<3.0.0` below Python 3.14 and `>=2.12.0,<3.0.0` from 3.14. Every allowed pydantic then supports the Python it is installed on, all eight matrix cells run, and the lock still holds one pydantic entry (finding 11). This is the approach packages that depend on numpy took to span numpy 1.26 and 2.

Alternatives: exclude the 3.14 lowest-direct cell, rejected because it would leave the floor misleading on 3.14; raise the floor to 2.12 everywhere, rejected because it would drop pydantic 2.11 users for no reason.

### The 3.11 failure is a library bug and is fixed there
`schema.py` imports `is_typeddict` from `typing_extensions`, a core dependency, which accepts both kinds of TypedDict, so the change is a strict superset: nothing accepted before is rejected. The fixture builds its TypedDict from `typing_extensions`, and a new test case covers the `typing` kind, skipped below 3.12 where pydantic itself rejects it. On Python below 3.12 a caller must still hand `from_schema` a `typing_extensions.TypedDict`, which is pydantic's own rule.

Alternatives: skip the test on 3.11, rejected because the package would claim 3.11 support while TypedDict input cannot work there; drop 3.11 from the matrix, rejected because it contradicts `requires-python`.

### Python 3.14 joins the classifiers
CI now tests it and it passes (finding 3), so the classifier is added in the same change.

### Actions are pinned to exact version tags
`astral-sh/setup-uv@v10.3.3`, `actions/checkout@v7.0.1`, `actions/cache@v6.1.0` and `actions/setup-node@v7.1.0`, with no comments, chosen by you. Dependabot's new `github-actions` ecosystem keeps them current. The exposure is small: a public repository, no secrets and a read-only token.

Alternatives: full commit SHAs with a trailing version comment, the strongest option but it needs a comment the project rules forbid; major tags such as `@v10`, rejected as the least pinned.

### Tool versions are pinned and cached
`setup-uv` installs uv 0.13.6, the version now pinned in the hook revision, and caches by `uv.lock`; the devcontainer pin moves to 0.13.6 in this change so all three agree. `actions/cache` keeps `~/.cache/pre-commit` keyed on the hook configuration. Node comes from `setup-node` and the OpenSpec CLI from `npx` at 1.15.0; the devcontainer pins the same version instead of `@latest`.

### The audit runs on a schedule
`audit.yml` runs `uv audit --locked --preview-features audit-command` weekly and on demand; `--locked` makes it audit the committed lock and fail if the lock is stale. A failure reaches you through GitHub's normal workflow notification. It does not block pull requests.

### Coverage is not gated yet
A floor at today's 31% would fail any pull request that adds untested backend code, and the backends are 0% until `test-streamlit-backend`. The follow-up is the roadmap item `add-coverage-gate`.

### A pull request template and a Dependabot ecosystem
`.github/pull_request_template.md` asks for the OpenSpec change and a short verification checklist. Dependabot gains a `github-actions` ecosystem on the same weekly schedule, with grouped minor and patch updates.

## Risks / Trade-offs

- [CI depends on the network: hook environments, PyPI, OSV for the audit] -> A failure is a re-run; the `ci` status makes it visible, not silent.
- [A new advisory fails an unrelated pull request] -> Treated as a signal; the scheduled audit and Dependabot reduce how often it surprises.
- [Python 3.14 is the newest version and dependencies may lag] -> It is in the matrix, so a lag fails visibly and the job can be reconsidered then.
- [Exact tags can in principle move] -> Small exposure here, and Dependabot reviews every bump; commit SHAs remain an option later.
- [The workflows cannot run locally] -> `actionlint` plus the change's own pull request run, which must be green before archive.
- [Dependabot may bump only one of the two pydantic lines] -> The lock remains the source of truth, and a lowest-direct cell fails visibly if a floor stops being installable.
- [The commit-message hook does not run in CI] -> The squash-merge setting is the real gate and is recorded as out of scope.

## Migration Plan

Land as separate commits in dependency order so each can be reverted alone: the fixture fix first so the matrix can be green, then the workflows, then the template and Dependabot, then the classifier, pin and documents. The pull request's own CI run is the final check. After the first green run, requiring `ci` on `main` is the roadmap item `protect-main-branch`, a repository setting rather than code. Rollback: revert the commits.
