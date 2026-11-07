# Proposal

## Why

The Streamlit backend is 1022 lines with 0% test coverage, and the `base.py` backend contract has none either (known issue 11). The `streamlit-backend` spec holds 17 requirements and 24 scenarios that nothing checks, so a change to `streamlit.py` can break documented behavior unnoticed. The manual harness, `test_wizard.py`, is untracked, sits where pytest collects it, and fails on import because `pydantic_extra_types` is declared nowhere (known issue 13). The coverage gate that follows on the roadmap cannot be set until the backends have tests.

Streamlit ships `AppTest` for exactly this. A spike on the current code showed it can drive the wizard (read widget labels, values, bounds and disabled state, set a value, rerun and read the returned dictionary) on Streamlit 1.47.0 (the declared floor) and 1.67.0, on Python 3.11 and 3.14.

## What Changes

- Add `tests/backends/` with a test for every scenario of the `streamlit-backend` spec, driven through `AppTest`, and a test for every scenario of the `wizard-backend` spec: the nine the base class implements run through a small in-test backend, so they need no Streamlit, and the four on submission and messages, which each backend implements, run through the Streamlit backend.
- Add two dependency groups, `test` (pytest and its plugins, moved out of `dev`) and `test-streamlit` (Streamlit's test needs), and include both in `dev`, so `uv sync` and `make test` work from a fresh clone and CI needs no extra flag. The Streamlit tests skip when Streamlit is missing, and a core-only run proves the rest of the suite does not depend on it.
- Add `pydantic-extra-types` to the `dev` group, for the harness.
- Replace the untracked root `test_wizard.py` with a tracked, working manual harness at `scripts/streamlit_harness.py`, runnable with one command and passing `ty`.
- Test the declared Streamlit floor on purpose: the lowest-direct cells resolve Streamlit 1.67.0, not the floor of 1.47.0, whatever the dependency layout (see the design), so a dedicated CI job runs the Streamlit tests against exactly 1.47.0.
- Update `AGENTS.md` (the layout lists `scripts/`, the tests description and the dependency groups), the README status and coverage badge with the measured figure, the roadmap (delete this item and refresh the coverage figure in `add-coverage-gate`).
- Correct one scenario of `streamlit-backend` with a delta spec. "Discriminated default" promised that the preselected alternative is "prefilled", but the alternative's other fields show their own defaults, not the values of the union's default (design finding 11). The scenario now says what is true, and the defect is recorded in the design and the roadmap.
- No library behavior changes. Any further scenario that does not hold on the current code is a spec defect and is handled the same way.

## Capabilities

### New Capabilities

None. This change adds tests, a harness and dependency configuration.

### Modified Capabilities

- `streamlit-backend`: the "Union fields" requirement, whose "Discriminated default" scenario is corrected to what the backend does. Every other requirement and scenario is verified as written.

## Impact

- New files: `tests/backends/conftest.py`, `tests/backends/test_base.py`, `tests/backends/test_streamlit.py`, `scripts/streamlit_harness.py`.
- Changed files: `pyproject.toml` and `uv.lock` (groups and `pydantic-extra-types`), `.github/workflows/ci.yml` (a core-only job, if the verified command works), `AGENTS.md`, `README.md`, `ROADMAP.md`.
- Removed: the untracked `test_wizard.py`, after its content is kept in the harness.
- Out of scope, each already its own roadmap item: the coverage gate (`add-coverage-gate`), the Streamlit collection defects (`fix-streamlit-collections`, known issues 3 to 7), the schema edge cases (`fix-schema-edge-cases`), and tests for the Typer and Textual backends, which do not exist yet.
