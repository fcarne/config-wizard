# Design

## Context

See `proposal.md` for motivation. Evidence from scratch runs on `main` (commit `7fd2ee2`); the repository was not touched.

| # | Finding | Evidence |
|---|---------|----------|
| 1 | The backends are untested | `config_wizard/backends/streamlit.py` is 1022 lines and `base.py` 209, both at 0%; `tests/` holds only `test_schema.py`, `test_mapper.py`, `test_utils.py` and `conftest.py`; total coverage is about 31% |
| 2 | The specs to cover | `streamlit-backend` has 17 requirements and 24 scenarios; `wizard-backend` has 8 requirements and 13 scenarios (resolve on construction, declaration order, default titles, empty schema, additional properties, output shape, submission, messages) |
| 3 | `AppTest` can drive the wizard | A scratch script using `AppTest.from_function` and `render_schema()` read `text_input`, `slider` (min 1, max 65535, step 1 from `ge=1, le=65535`), `toggle`, `selectbox` options and value, and `button` labels with their disabled state, set a text value, reran and saw it in the returned dictionary. It ran identically on Streamlit 1.47.0 and 1.66.1 or 1.67.0 on Python 3.11 and 3.14 |
| 4 | The wizard's return value needs a channel | `AppTest` has no return channel, so the app function stores `render_schema()` or `render_wizard()` output in `st.session_state` |
| 5 | The lowest-direct cells do not test the Streamlit floor, whatever the layout | `uv lock --resolution lowest-direct` and `uv run --isolated --resolution lowest-direct` resolve Streamlit 1.67.0 with the requirement in the extra only, in a group included by `dev`, in `dev` directly, in the group alone, and on a fresh lock. The same requirement as `==1.47.0` locks cleanly and the resolver does select 1.47.0 first and then abandons it. With the upper bound at `<1.67.0` or lower it keeps 1.47.0; with `<1.67.1` or higher it picks 1.67.0 although 1.47.0 is allowed. A `packaging<26` constraint changes nothing. The cause is not understood; `pydantic-extra-types` does resolve to its floor (2.10.0) in the same runs. `uv run --with "streamlit==1.47.0"` does override the synced Streamlit (1.47.0 on 3.12, and on 3.14 with `--isolated`) |
| 6 | `scripts/` already exists and is type-checked | It holds `check_commit_msg.py`; `[tool.ty.src]` includes `scripts`, so the harness must pass `ty` |
| 7 | The harness will not pass `ty` as written | `test_wizard.py` annotates fields with calls such as `pydantic.conint(gt=0, lt=100)` and `pydantic.constr(...)`, which are not valid type expressions |
| 8 | `pytest` options | `addopts` always adds branch coverage for `config_wizard`; `make test` runs `pytest tests/`; CI runs `pytest tests` |
| 9 | The harness imports `pydantic_extra_types.color` and `.payment` | Both are in the base package of `pydantic-extra-types`, with no extra needed. The lowest version compatible with pydantic 2.11.7 on Python 3.11 to 3.14 is not yet known |
| 10 | A defect found while writing the tests, not in the baseline list | In a set of integers, pressing `Add Item` twice and typing `1` in both rows shows the duplicate-items error and returns `{1}` on that rerun, as the scenario says. On the next rerun the duplicate row is gone, because the row count follows the stored, de-duplicated set. The scenario holds, so the spec stays as written; the defect goes to `fix-streamlit-collections` |
| 11 | A scenario that does not hold | "Discriminated default" says the preselected alternative is "prefilled". With a pydantic union `A | B` discriminated on `type` and a default `B(age=7)`, `B` is preselected and `type` shows `B`, but `age` shows 0. `_render_union_input` assigns the whole default to the selected alternative's schema, and the object renderer then fills each field from that field's own default, never from the default mapping's values |

Constraints that shape the approach:
- The backend is optional. The core must install, import and pass its tests without Streamlit.
- The spec rule is "verified behavior only": a scenario that fails on the current code means the spec is wrong, not that the test should be bent or marked as expected to fail.
- The project rules forbid explanatory comments, and the tests should read like the existing ones (plain `test_<unit>__<case>__<result>` names, fixtures in `conftest.py`).

## Goals / Non-Goals

**Goals:**
- Every scenario of `streamlit-backend` and `wizard-backend` has a test that fails if the behavior breaks.
- The suite runs from a fresh clone with `make install` and `make test` and in CI on every cell, and the Streamlit floor is exercised by a dedicated job.
- A contributor can look at the wizard in a browser with one command.

**Non-Goals:**
- A coverage gate, fixing the collection defects (known issues 3 to 7), the date, time and path widgets (known issue 1), required-field enforcement (known issue 8), and tests for backends that do not exist.
- Pixel-level or browser end-to-end tests; `AppTest` covers behavior, the harness covers appearance.

## Decisions

### Layout: `tests/backends/` with one shared app helper
`tests/backends/test_base.py` drives the base class through a minimal in-test subclass that holds state in a dictionary and records what it is asked to render, so it needs no Streamlit. It covers the nine `wizard-backend` scenarios the base class implements; submission and messages are abstract there, so those four scenarios are tested through the Streamlit backend. `tests/backends/test_streamlit.py` starts with `pytest.importorskip("streamlit")` and drives the real backend. `tests/backends/conftest.py` holds one helper that builds an `AppTest` from a single app function taking the schema source and render options through `args`, stores the result in `st.session_state`, and runs it with a generous timeout. Test models live at module level in the test file, so they are defined once and passed in.

Alternative: one script per scenario. Rejected: it multiplies boilerplate and hides the schema from the test that uses it.

### `test` and `test-streamlit` groups, included by `dev`
`[dependency-groups]` gains `test` (pytest, pytest-cov and pytest-mock, moved out of `dev`) and `test-streamlit` (`streamlit` with the same bounds as the extra), and `dev` includes both with `include-group`, next to `pydantic-extra-types` (for the harness) and the lint and type tools. `uv sync` therefore installs everything for tests, CI needs no `--all-extras`, and a future Typer or Textual backend gets its own group the same way. The bound is written in two places (the extra and the group), which is accepted; a self-reference from the group to the extra was not tried, because the layout turned out not to affect the resolution (finding 5).

Alternatives: put `streamlit` straight into `dev` (simplest, but the core cannot be tested without it and each backend lengthens `dev`); pass `--all-extras` in CI and `make test` (easy to forget).

### Prove the core stands alone
A core-only run (Streamlit not installed and not importable) must pass with the Streamlit tests skipped. With `dev` including `test-streamlit`, `--no-group test-streamlit` does not remove it, and `--no-dev` removes pytest as well; that is why pytest lives in its own `test` group. The command is `uv run --isolated --no-dev --group test pytest tests` (`--isolated` so a local venv that already holds Streamlit cannot hide a leak, the same as in CI): in a scratch copy it left Streamlit absent and pytest present and gave 107 passed and 29 skipped (the Streamlit tests). A CI job `core`, which `ci` waits for, runs it, so a stray Streamlit import in the core is caught.

### The Streamlit floor gets its own CI job
A job `streamlit-floor` (Python 3.12) runs `uv run --python 3.12 --with "streamlit==1.47.0" pytest tests/backends`, and the `ci` job waits for it. The lowest-direct cells keep running the Streamlit tests, against the newest Streamlit, so the floor is tested explicitly instead of through resolver behavior that could not be explained or relied on (finding 5). When the extra's floor is raised, the pin in this job is raised with it; the job's own check that the Streamlit it ran is 1.47.0 is part of its verification.

Alternatives: cap Streamlit below `1.67.1` so lowest-direct picks the floor (rejected: a cap that follows a release number is wrong for users and needs raising every release); accept that the floor is untested (rejected: it was one of the reasons for the group).

### A failing scenario is a spec defect, not a test to excuse
If a scenario does not hold, work stops. The options are a MODIFIED delta to the spec in this change, or recording the defect here when the scenario was never meant to be verified. No `xfail`, no skip. This happened once (finding 11): the maintainer chose to correct the scenario, so the change carries a delta for `streamlit-backend` and no longer sets `skip_specs`. The delta says only what is true (the alternative is preselected and its discriminator field shows the value); the ignored default values are a defect and live here and in the roadmap, not in the requirement.

### The harness moves to `scripts/streamlit_harness.py` and is fixed
Its content moves unchanged except where `ty` and the imports require it: the `conint` and `constr` annotations become `Annotated[..., Field(...)]`, and its dependencies are all in the `dev` group. It runs with `uv run streamlit run scripts/streamlit_harness.py`. The untracked original is copied to the session scratchpad first and removed from the repository root only after the harness works, since an untracked file cannot be restored from git. `experiments/` stays the maintainer's gitignored scratch and is not touched.

### Coverage is reported, not gated
The change records the coverage after the tests land and updates the README badge and the roadmap figure. Setting a floor stays in `add-coverage-gate`. How much of `streamlit.py` the `AppTest` runs report depends on coverage following Streamlit's script thread, which is checked early in the work.

## Risks / Trade-offs

- [`AppTest` runs may not be counted by coverage] → Check `streamlit.py` coverage is above 0 after the first test and, if it is not, fix the coverage configuration (for example thread concurrency) before writing the rest.
- [A scenario fails on the current code] → Pause per the decision above; the cost is a spec delta and a longer change.
- [The Streamlit floor fails the suite] → The spike passed on 1.47.0 for 3.11 and 3.14, but the full suite on the `streamlit-floor` job is the real test; if it fails, raise the floor in the extra and the group together and record why. The job runs on one Python version, so a floor failure specific to another version would not be seen.
- [`pydantic-extra-types` at its lowest bound breaks on 3.14 or with pydantic 2.11.7] → Pick the bound by running the lowest-direct cells for 3.11 and 3.14, as was done for pydantic.
- [Streamlit widget internals change between 1.47 and 1.6x] → The tests assert on documented `AppTest` properties (label, value, options, disabled, min, max), not on protos; if one differs by version it is handled in the helper.

## Migration Plan

Nothing to deploy: tests, a dev group, a script and documentation. Rollback is reverting the pull request. The one irreversible step is deleting the untracked `test_wizard.py`, which happens last, after a copy sits in the scratchpad and the harness has run.
