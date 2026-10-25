# Proposal

## Why

The project's only description of itself is `DESIGN.md`, an early vision document that no longer matches the code: it describes a `FormField` model, a CLI, an exporter and three backends, while the code ships a JSON-Schema-native core and a single Streamlit backend. With no specs and no agent guidance, every new change has to rediscover what exists. Capturing the implemented behavior as baseline specs, plus durable project and agent documents, lets `DESIGN.md` be retired and future work proceed through OpenSpec changes.

## What Changes

- Add baseline specs that describe current, observable behavior of the implemented modules, as verified against the code and the passing test suite. No runtime behavior changes.
- Record the real architecture and the known gaps found while baselining (unreachable date/time/path widgets, unresolvable `$defs`-less JSON specs, inverted clear-button state, unenforced required fields, broken console-script entry point) in `design.md`, to be addressed by follow-up changes.
- Add `AGENTS.md` as the canonical guide for coding agents and `CLAUDE.md` as a single import of it.
- Add `CONSTITUTION.md` holding the project's durable principles, conventions (including Google-style docstrings) and non-goals.
- Rewrite `README.md` so implemented features and planned features are clearly separated.
- Add a short `context:` entry to `openspec/config.yaml` pointing at the constitution.
- **Remove `DESIGN.md`.** Its still-valid intent moves to `CONSTITUTION.md` and `README.md`; its outdated architecture is superseded by the specs and this change's `design.md`.

## Capabilities

### New Capabilities

- `schema-loading`: Building a settings schema from a Pydantic model, dataclass, TypedDict, or a JSON Schema / OpenAPI schema dictionary, including capture of reusable definitions.
- `schema-resolution`: Inlining `$ref` references into a self-contained schema, and the failure modes for missing definitions, missing reference maps and circular references.
- `input-type-mapping`: Classifying a schema property into an input kind (text variants, numbers, boolean, enum, collections, objects, unions, any, null) that backends use to choose a widget.
- `wizard-backend`: The contract every interactive backend follows: schema resolution on construction, property traversal order, default titles, additional-properties handling and output shape.
- `streamlit-backend`: The Streamlit wizard: the widget used per input kind, constraint handling, collection editing, union selection, inline validation feedback and form submission.

### Modified Capabilities

None. The project has no existing specs.

## Impact

- Code: none. `config_wizard/` and `tests/` are untouched.
- Documentation: adds `AGENTS.md`, `CLAUDE.md`, `CONSTITUTION.md`; rewrites `README.md`; deletes `DESIGN.md`.
- Tooling: `openspec/config.yaml` gains a `context:` entry; `openspec/specs/` is populated when this change is archived.
- Out of scope: the CLI, exporter, final validation step, Typer and Textual backends, and fixes for the known gaps. Each becomes its own change.
