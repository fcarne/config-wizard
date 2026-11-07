# Tasks

## 1. Dependencies and the test helper

- [x] 1.1 In `pyproject.toml`, add the `test-streamlit` dependency group (`streamlit` with the extra's bounds), include it in `dev` with `include-group`, and add `pydantic-extra-types` to `dev`. Choose the `pydantic-extra-types` lower bound by running `uv run --isolated --resolution lowest-direct --python <3.11 and 3.14> python -c "import pydantic_extra_types.color, pydantic_extra_types.payment"`. Run `uv lock`. Verify `uv lock --check` passes, `uv sync` installs Streamlit and `pydantic-extra-types` without `--all-extras`, and the lowest-direct resolution on 3.11 and 3.14 reports `pydantic-extra-types` 2.10.0 and imports both modules (it resolves Streamlit 1.67.0, which is expected, see the design).
- [x] 1.2 Create `tests/backends/conftest.py` with the shared `AppTest` helper (one app function taking the schema source and render options through `args`, storing the result in `st.session_state`, a generous default timeout), and write the first Streamlit test (the scalar fields scenario of "Common field presentation": a string property with `default: "localhost"` and `readOnly: true` renders a disabled text field showing `localhost`) in `tests/backends/test_streamlit.py` starting with `pytest.importorskip("streamlit")`. Verify that test passes with `uv run pytest tests/backends` and `streamlit.py` coverage is above 0% in the report; if it is 0%, fix the coverage configuration before continuing.
- [x] 1.3 In `pyproject.toml`, add `[tool.coverage.run]` with `branch = true`, and remove the `--cov-branch` flag from the pytest `addopts` and from `make test`, so branch coverage is set in one place. Verify `uv run pytest tests` and `make test` still print the `Branch` and `BrPart` columns with the same totals as before the move (`base.py` and `streamlit.py` rows included), and `grep -rn "cov-branch" pyproject.toml Makefile .github` finds nothing.

## 2. The base contract (no Streamlit)

- [x] 2.1 Create `tests/backends/test_base.py` with a minimal in-test backend and a test for each of the nine `wizard-backend` scenarios the base class implements: resolve on construction (unresolved and unresolvable), declaration order and the required flag, default titles for snake and camel case keys, empty schema, additional properties (top level and nested flattened) and output shape for a nested object. The four scenarios on submission and messages are abstract in the base class and are covered through Streamlit in 3.1. Verify every one of the nine has a test whose name says so, `uv run pytest tests/backends/test_base.py` passes (9 passed), and `base.py` coverage is reported (97%).

## 3. The Streamlit backend scenarios

- [x] 3.1 Cover the form and presentation requirements: isolated wizard state (two wizards with keys `a` and `b`), form layout and submission (default form with the `AppSettings` subheader and `Save`), formless rendering (live values), and common field presentation (label, help, default, placeholder, read-only), plus the four `wizard-backend` scenarios the base class leaves to each backend: submission (not yet submitted, and submitted with a submit function) and messages (titled warning, empty message). Verify each scenario has a test and `uv run pytest tests/backends/test_streamlit.py` passes.
- [x] 3.2 Cover the scalar fields: enum (several options with the default selected, single option with no widget and the value returned), boolean toggle, numeric (bounded integer slider 1 to 10 step 1, exclusive bound giving a number field with minimum 1), text (password masked) and inline format validation (invalid email message with the entered value returned, custom pattern error). Verify each scenario has a test and the file passes.
- [x] 3.3 Cover the collection fields: sequences (adding an item, tuple items by position), size limits (`Add Item` disabled at `maxItems`), set uniqueness (duplicate error and `{1}` returned), dictionaries (new row key `new_item_2`, default entries `a`=1 and `b`=2) and object fields (a `Db` heading before `Host` and `Port`). These render without a form, as the spec says. Verify each scenario has a test and the file passes.
- [x] 3.4 Cover unions and the remaining kinds: discriminated default preselected with its `type` field showing the value (the scenario corrected by this change's delta), optional integer selector offering `integer` and `null`, free-form fields (valid JSON returned as a mapping, invalid JSON error with the raw text returned) and null fields (nothing shown, value null). Verify each scenario has a test and the file passes.
- [x] 3.5 Verify full coverage of the spec: list every `#### Scenario:` of `streamlit-backend` (24) and `wizard-backend` (13) and match each to a test by name. Verify no scenario is unmatched, none is skipped or marked as expected to fail, and `uv run pytest tests` passes on Python 3.11 and 3.14. If any scenario fails on the current code, stop and handle it as the design says.

## 4. The core without Streamlit and the Streamlit floor

- [x] 4.1 In `pyproject.toml`, move pytest, pytest-cov and pytest-mock from `dev` into a new `test` group that `dev` includes (next to `test-streamlit`), and run `uv lock`. Verify `uv lock --check` passes, `uv sync` still installs pytest and Streamlit, and `uv run --isolated --no-dev --group test pytest tests` runs with Streamlit absent (`importlib.util.find_spec("streamlit")` is None) and reports 107 passed and 29 skipped.
- [x] 4.2 In `.github/workflows/ci.yml`, add a job `core` (Python 3.12) with a step that fails if Streamlit is importable and a step running `uv run --isolated --no-dev --group test pytest tests`, and make the `ci` job wait for it and fail unless it succeeded. Verify `uvx --from actionlint-py actionlint .github/workflows/ci.yml` reports nothing and `uv run pre-commit run check-yaml --files .github/workflows/ci.yml` passes; the job itself is proven by the pull request's CI run.

- [x] 4.3 In `.github/workflows/ci.yml`, add a job `streamlit-floor` (Python 3.12) running `uv run --python 3.12 --with "streamlit==1.47.0" pytest tests/backends`, preceded by a step that fails unless the Streamlit imported in that environment is 1.47.0, and make the `ci` job wait for it. Verify the same two commands pass locally with Streamlit 1.47.0 reported, actionlint reports nothing and `check-yaml` passes; the job itself is proven by the pull request's CI run.

## 5. The manual harness

- [x] 5.1 Copy `test_wizard.py` to the session scratchpad, then create `scripts/streamlit_harness.py` with the same fields, replacing the `conint` and `constr` annotations with `Annotated[..., Field(...)]`. Verify `uv run ty check scripts` reports nothing, and `uv run streamlit run scripts/streamlit_harness.py --server.headless true` starts and serves `http://localhost:8501` with an HTTP 200 (stop it afterwards).
- [ ] 5.2 Remove the root `test_wizard.py`. Verify `git status --short` shows no untracked file, `pytest` run from the repository root with no path argument collects nothing from it, and the scratchpad copy still exists.

## 6. Documents and roadmap

- [ ] 6.1 Run `uv run pytest tests` and record the total coverage and the coverage of `base.py` and `streamlit.py`. Update the README status paragraph (the backends now have tests) and the coverage badge with the measured total, in `AGENTS.md` update the layout (`tests/backends/`, `scripts/`), the tests description and the mention of dependency groups, and in `ROADMAP.md` delete the `test-streamlit-backend` item, renumber the rest, and replace the coverage figure in `add-coverage-gate`, and add the set-row defect (finding 10) and the ignored union default values (finding 11) to the `fix-streamlit-collections` item. Verify the numbers in the three files equal the recorded ones, the roadmap numbering is consecutive from 1, and `uv run pre-commit run --all-files` passes.
- [ ] 6.2 Run `openspec validate test-streamlit-backend --strict` and `openspec validate --all --strict`. Verify both report valid and the change shows one MODIFIED requirement for `streamlit-backend`.

## 7. Integration checks

- [ ] 7.1 Clone the branch into an empty directory under the session scratchpad and run `make install`, `make test`, `make lint` and `uv run --isolated --resolution lowest-direct --python 3.14 pytest tests`. Verify all pass and `git status --short` is empty afterwards, and that `uv run --python 3.12 --with "streamlit==1.47.0" pytest tests/backends` passes there too.
- [ ] 7.2 Run `git diff --name-status origin/main..HEAD` and verify the only changes are `tests/backends/*`, `scripts/streamlit_harness.py`, `pyproject.toml`, `uv.lock`, `.github/workflows/ci.yml` (only if 4.2 applied), `AGENTS.md`, `README.md`, `ROADMAP.md` and the change directory.
- [ ] 7.3 Push the branch, open the pull request, and wait for its CI run. Verify `gh pr checks` shows `checks`, `core` (if added), `streamlit-floor`, all eight `tests` cells and `ci` passing.

## Workflow follow-up

- Archive the change once its CI run is green; the archive pull request goes through the `protect-main` ruleset like every other.
- Continue with `add-coverage-gate`, using the coverage recorded in 6.1.
