# Tasks

## 1. The coverage floor

- [x] 1.1 In `pyproject.toml`, add `fail_under = 84` to `[tool.coverage.report]`. Verify `uv run pytest tests` prints "Required test coverage of 84.0% reached" and exits 0, `uv run pytest tests --cov-fail-under=99` exits 1 with "FAIL Required test coverage of 99.0% not reached", `make test` prints the same "reached" line, and the full suite passes the floor with both resolutions on Python 3.11, 3.12, 3.13 and 3.14 (`uv run --isolated [--resolution lowest-direct] --python <version> pytest tests` exits 0 in all eight cases).
- [ ] 1.2 In `.github/workflows/ci.yml`, add `--no-cov` to the pytest commands of the `core` and `streamlit-floor` jobs. Verify `uv run --isolated --python 3.12 --no-dev --group test pytest tests --no-cov` and `uv run --python 3.12 --with "streamlit==1.47.0" pytest tests/backends --no-cov` exit 0 and print no coverage table, `uvx --from actionlint-py actionlint .github/workflows/ci.yml` reports nothing, and `uv run pre-commit run check-yaml --files .github/workflows/ci.yml` passes.

## 2. The badge script

- [ ] 2.1 Create `scripts/coverage_badge.py`: a function that turns a percentage into the endpoint mapping (`schemaVersion` 1, label `coverage`, message the rounded percentage with `%`, color `brightgreen` from 90, `yellowgreen` from 80, `yellow` from 70, otherwise `red`) and a command line entry taking the coverage.py JSON path and the output path. Verify by running it on sample coverage JSON files holding 95, 85, 75 and 50 percent that the outputs are `brightgreen`/`95%`, `yellowgreen`/`85%`, `yellow`/`75%` and `red`/`50%`, that a real `uv run coverage json` file after `uv run pytest tests` gives `85%`, and that `uv run ruff check scripts`, `uv run ruff format --check scripts` and `uv run --all-extras ty check` pass.

## 3. The badge job

- [ ] 3.1 In `.github/workflows/ci.yml`, add the job `coverage-badge` as designed: `needs: tests`, a condition that it runs only on `main` for pushes and manual runs, `permissions: contents: write` on the job, a timeout, checkout, setup-uv at 0.13.6, the suite and `coverage json` on Python 3.12, the script writing the endpoint file outside the working tree, and a publish step that switches to an orphan `badges` branch, adds only `coverage.json`, commits as `github-actions[bot]` with a single-line subject, and force-pushes. Leave the `ci` job's `needs` unchanged. Verify actionlint reports nothing and `check-yaml` passes.
- [ ] 3.2 Rehearse the publish step: in a scratch clone with a local bare repository as `origin`, run its exact commands twice with different sample files. Verify `badges` exists on the remote after each run with exactly one commit that contains only `coverage.json`, the second run replaces the first without error, and the working branch is untouched.

## 4. Documents and roadmap

- [ ] 4.1 In `README.md`, replace the static coverage badge with `https://img.shields.io/endpoint?url=` followed by the percent-encoded raw URL of `badges/coverage.json` and adjust the status sentence to say the figure is measured on `main` and gated in CI. In `AGENTS.md`, add the floor (`fail_under` in `[tool.coverage.report]`, raised by pull request), the `--no-cov` exceptions, the `coverage-badge` job and the `badges` branch. In `ROADMAP.md`, delete the `add-coverage-gate` item and renumber the rest. Verify decoding the README URL gives `https://raw.githubusercontent.com/fcarne/config-wizard/badges/coverage.json`, the roadmap numbering is consecutive from 1, and `uv run pre-commit run --all-files` passes.
- [ ] 4.2 Run `openspec validate add-coverage-gate --strict` and `openspec validate --all --strict`. Verify both report valid.

## 5. Integration checks

- [ ] 5.1 Clone the branch into an empty directory under the session scratchpad and run `make install`, `make test`, `make lint`, `uv run --isolated --resolution lowest-direct --python 3.14 pytest tests`, the `core` and `streamlit-floor` commands with `--no-cov`, and the badge script on a fresh `coverage json` from `uv run --python 3.12 pytest tests`. Verify everything passes, the script prints `85%` for Python 3.12, and `git status --short` is empty afterwards.
- [ ] 5.2 Run `git diff --name-status origin/main..HEAD` and verify the only changes are `pyproject.toml`, `.github/workflows/ci.yml`, `scripts/coverage_badge.py`, `README.md`, `AGENTS.md`, `ROADMAP.md` and the change directory.
- [ ] 5.3 Push the branch, open the pull request, and wait for its CI run. Verify `gh pr checks` shows `checks`, `core`, `streamlit-floor`, all eight `tests` cells and `ci` passing, and the `coverage-badge` job skipped.

## 6. After the merge

- [ ] 6.1 Run `gh workflow run ci.yml --ref main` and wait for the run. Verify the `coverage-badge` job succeeded, `git ls-remote origin badges` shows the branch, `https://raw.githubusercontent.com/fcarne/config-wizard/badges/coverage.json` returns JSON with `schemaVersion` 1, label `coverage` and a message matching `^[0-9]+%$`, and the badge URL from the README returns an SVG containing `coverage` and that percentage.
- [ ] 6.2 If any check in 6.1 fails (most likely the job's `contents: write` permission), diagnose it from the run log and fix it in a follow-up pull request before archiving. Verify by repeating 6.1.

## Workflow follow-up

- Archive the change once 6.1 passes; the archive pull request goes through the floor and the ruleset like every other.
- Continue with `fix-streamlit-collections`, which adds tests as it fixes defects and should raise the floor as coverage grows.
