# Design

## Context

See `proposal.md` for motivation. The implemented system is smaller than `DESIGN.md` describes:

```
[Pydantic model | dataclass | TypedDict]      [JSON Schema / OpenAPI dict]
                 |                                       |
                 v                                       v
          SettingsSchema.from_schema            SettingsSchema.from_spec
                 \                                      /
                  +---------> SettingsSchema <---------+
                                (ref_map = $defs)
                                     |
                                     | resolve_refs()
                                     v
                           ResolvedSettingsSchema
                                     |
                                     | property_to_input_type()  (mapper.py, InputType)
                                     v
                     SettingsWizardBackend (backends/base.py, ABC)
                                     |
                                     v
                     StreamlitSettingsWizard (backends/streamlit.py)
                                     |
                                     v
                          dict of user values  --> caller's submit_fn
```

Not present: `cli.py`, `loader.py`, `validator.py`, `exporter.py`, `types.py`, and any `FormField` model. `backends/typer.py` and `backends/textual.py` are empty files. `pyproject.toml` still declares `config-wizard = "config_wizard.cli:main"`.

Test evidence at baseline time: 98 passing tests across `tests/test_schema.py`, `tests/test_mapper.py` and `tests/test_utils.py`. `backends/base.py` and `backends/streamlit.py` have no automated tests; Streamlit behavior in the specs was checked with Streamlit's `AppTest` harness during exploration and against the manual harness `test_wizard.py`.

## Goals / Non-Goals

**Goals:**
- Specs that a reader can check against the current code and that a future test suite can turn into tests one scenario at a time.
- One place for agent guidance (`AGENTS.md`) shared by Claude Code and opencode.
- A durable statement of principles (`CONSTITUTION.md`) that outlives any single change.

**Non-Goals:**
- Fixing any defect listed below.
- Specifying planned features (CLI, exporter, validation step, Typer, Textual).
- Adding tests for the backends; that work belongs to the follow-up changes that fix their defects.

## Decisions

### Specs describe verified behavior; defects stay unspecified
A requirement is written only for behavior that was observed to work. Where code behavior is clearly a defect, the spec does not state it as a requirement, nor contradict it, and the defect is listed under Known Issues. Where behavior is a limitation rather than a defect (for example date formats classifying as text), the spec states it, so the follow-up change shows up as a MODIFIED requirement.

Alternative considered: specifying intended behavior. Rejected because the baseline would be false on day one and archive would claim behavior the code lacks.

### Five capabilities, split along module seams
`schema-loading`, `schema-resolution`, `input-type-mapping`, `wizard-backend`, `streamlit-backend`. Loading and resolution are separate because their failure modes and callers differ; the backend contract is separate from Streamlit so a Typer or Textual change adds a sibling capability instead of modifying a Streamlit one. Text-case helpers in `utils.py` are not a capability; their observable effect (default labels) lives in `wizard-backend`.

### The architecture is JSON-Schema-native
The `FormField` intermediate model from `DESIGN.md` is abandoned. Backends walk `ResolvedSchema` objects (an OpenAPI 3.1 schema object with every `$ref` inlined and missing `type` defaulted to `object`) and dispatch on `InputType`. This is recorded in `AGENTS.md` and `CONSTITUTION.md` so new backends follow it.

### `AGENTS.md` is canonical, `CLAUDE.md` imports it
`CLAUDE.md` contains only `@AGENTS.md`. Both Claude Code and opencode are configured in this repository (`.claude/`, `.opencode/`), and a single file avoids drift.

### `CONSTITUTION.md` holds principles, `AGENTS.md` holds procedure
Constitution: purpose, architectural principles, conventions (Google-style docstrings, typing, 120-column Ruff, tests per behavior), non-goals, and how changes flow through OpenSpec. AGENTS.md: commands (`make install|format|lint|test`), layout, where specs live, how to verify work. `openspec/config.yaml` gets a short `context:` pointing at the constitution rather than copying it.

### Glossary lives in `CONSTITUTION.md`, rules live in `config.yaml`
Specs avoid code names on purpose, so the mapping from behavior vocabulary to code (input kind to `InputType`, settings schema to `SettingsSchema`, resolved schema to `ResolvedSettingsSchema`, backend to `SettingsWizardBackend`) is kept once, in the constitution, where agents already look. The baseline policy is encoded as `rules:` in `openspec/config.yaml` so it is applied at artifact-writing time instead of relying on memory.

Alternative considered: a separate `GLOSSARY.md`. Rejected as one more file to keep in sync for about ten entries.

### Shared agent settings are narrow
`.claude/settings.json` allows `make` targets, `openspec`, `poetry run pytest|ruff|mypy` and read-only git commands. It does not allow a blanket `poetry run *`, which would permit arbitrary code. Personal overrides go in `.claude/settings.local.json`, which is git-ignored.

### `DESIGN.md` is committed, then deleted
It is untracked, so git cannot restore it. The apply branch commits it first and deletes it later, so history keeps it. Content mapping: overview and input formats go to `README.md`; vision, non-goals and the roadmap list go to `CONSTITUTION.md` and `README.md`; the architecture section is superseded by this document and the specs; the name-origin and authorship notes are dropped.

## Known Issues

Each item below is a candidate follow-up change.

| # | Area | Observed behavior | Evidence |
|---|------|-------------------|----------|
| 1 | input-type-mapping | `format` `date`, `date-time`, `time`, `duration`, `path` classify as text, so Streamlit's date, time, datetime and path widgets are unreachable | Pydantic `date`, `datetime`, `time`, `timedelta`, `Path` fields all map to `TEXT` |
| 2 | input-type-mapping | A single-value `Literal`, emitted as `const`, classifies as text, so discriminator fields render as editable text instead of being fixed | `Literal["only"]` maps to `TEXT`; the single-option enum shortcut never triggers for discriminators |
| 3 | streamlit-backend | `render_wizard` wraps fields in `st.form`, but sequence, dict and additional-properties fields use `st.button`, which Streamlit forbids inside forms | `StreamlitAPIException: st.button() can't be used in an st.form()` for a `dict[str, int]` field |
| 4 | streamlit-backend | Renaming a dict key to a new name is ignored; renaming onto an existing key overwrites it and drops a row | `{"a":1,"b":2}`, rename `b` to `c` returns `{"a":1,"b":2}`; rename `b` to `a` returns `{"a":2}` |
| 5 | streamlit-backend | Sequence item defaults are not shown: `[5]` renders one empty row and returns `[None]`; item labels show the internal key instead of `Item #n` | `_render_list_item_input` builds `item_property_schema` but renders the original schema |
| 6 | streamlit-backend | `Remove` ignores `minItems`, because the check reads the item schema instead of the sequence schema | List with `min_length=1` and one row has `Remove` enabled |
| 7 | streamlit-backend | `Clear Items` is disabled on editable fields and enabled on read-only ones | `_is_clear_button_disabled` returns the inverse |
| 8 | streamlit-backend | `required` is passed but never enforced; empty required fields return `None` | Unused parameter in `_render_property` |
| 9 | schema-resolution | A schema document without `$defs` cannot be resolved even when it contains no `$ref`, so it cannot be given to a backend | `from_spec({"type":"object",...}).resolve_refs()` raises `ValueError` |
| 10 | packaging | Console script points to the missing `config_wizard.cli:main` | `pyproject.toml` `[project.scripts]` |
| 11 | testing | Backends have no automated tests; measured coverage is 30% (`base.py` and `streamlit.py` at 0%) while the README badge claims 100% | `pytest --cov` run |
| 12 | tooling | No CI: lint, types, tests and `openspec validate` are not enforced on pull requests | `.github/` is empty |

## Risks / Trade-offs

- [Specs encode limitations, so fixes appear as spec changes] -> Intended: each fix is a reviewable MODIFIED requirement with its own tests.
- [Streamlit scenarios were verified manually, not by committed tests] -> Known Issue 11; the first Streamlit fix change adds an `AppTest`-based suite covering the existing scenarios.
- [Deleting an untracked file] -> It is committed before deletion, so history keeps it.
- [Agent instructions drift from code] -> `AGENTS.md` lists only commands and paths that exist; tasks verify each command runs.

## Migration Plan

1. Write the new documents and `config.yaml` context.
2. Commit `DESIGN.md` as the branch's first commit, then delete it once its content has moved.
3. Validate the change and archive it, which creates `openspec/specs/<capability>/spec.md` for all five capabilities.

Rollback: restore `DESIGN.md` from the commit that preserved it, delete the new root documents, revert `README.md` and `openspec/config.yaml` with git, and remove the archived specs directory entries.
