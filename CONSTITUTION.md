# Constitution

Durable principles for `config-wizard`. Behavior lives in `openspec/specs/`; this file holds what stays true across changes. Procedure and commands live in `AGENTS.md`.

## Purpose

Take a configuration schema or class, walk the user through an interactive wizard, and produce a valid configuration for the caller to use. The library is framework-agnostic: the schema handling is shared and each UI toolkit is a backend.

## Architectural principles

1. **JSON-Schema-native core.** Schemas are held as OpenAPI 3.1 schema objects (`SettingsSchema`) and walked after every `$ref` is inlined (`ResolvedSettingsSchema`). There is no intermediate form model. Anything a backend needs to know comes from the schema.
2. **One dispatch vocabulary.** `InputType` and `property_to_input_type` decide what kind of input a property is. Backends choose widgets from that decision and never re-derive it from raw schema keys.
3. **Backends implement one contract.** Every UI toolkit subclasses `SettingsWizardBackend`. Shared behavior (resolution on construction, property order, default titles, additional-properties handling, output shape) lives in the base class, not in each backend.
4. **The core knows no UI.** Modules outside `config_wizard/backends/` never import a UI toolkit. A backend module imports only its own toolkit.
5. **Specs describe behavior, not code.** Specs use the vocabulary in the glossary below and avoid class and function names, so internals can change without a spec change.

## Dependencies

- **Core:** Pydantic (with the email extra), `openapi-pydantic`, `jsonschema` and `typing-extensions`, all declared as `dependencies` in the `[project]` table. `pydantic-settings` is also declared there for the planned settings-class loading and is not imported yet.
- **Optional:** every UI toolkit and the docs tooling is an extra in `[project.optional-dependencies]`: `streamlit`, `cli` (Typer and Rich), `textual` and `docs`. A UI toolkit is never added to the core dependencies.
- **Development tools:** pytest, pytest-cov, pytest-mock, pre-commit, ruff and mypy are the `dev` group in `[dependency-groups]`, which `poetry install` installs by default.
- Exact versions live in `pyproject.toml` and are not repeated in prose.

## Conventions

- **Python:** 3.11 and newer. Code is upgraded with `pyupgrade --py310-plus`.
- **Types:** full type hints, checked by mypy with the Pydantic plugin. Suppressions such as `type: ignore` are narrow and carry the error code.
- **Style:** Ruff for linting and formatting at 120 columns, run through pre-commit. Lint rules are fixed in the code and are not ignored or disabled to make a change pass.
- **Docstrings:** Google style on public and private functions, methods and classes, with `Args:`, `Returns:` and `Raises:` sections where they apply, written as `name (type): description`.
- **Tests:** pytest, one test per spec scenario. Test names follow `test_<unit>__<condition>__<expected>` and every test has a one-line docstring. Parametrize instead of copying a test.
- **Commits:** see `AGENTS.md`.

## Non-goals

- A schema language of its own. JSON Schema and OpenAPI are the input formats.
- Replacing Pydantic validation. The wizard collects values and leaves validation of the final result to the caller's models.
- A toolkit-neutral widget abstraction beyond `SettingsWizardBackend`. Each backend maps input kinds to its own widgets.

## Change workflow

Behavior changes go through an OpenSpec change: explore, propose, apply, archive. The change's specs are the contract and its tasks name how each step is verified. Known defects are recorded in a change's `design.md` and fixed by their own change, not folded into unrelated work. What is planned is tracked in `ROADMAP.md`; each item becomes a change when it is started.

## Glossary

Specs use the behavior term on the left; code uses the name on the right.

| Behavior term | Code name |
|---|---|
| input kind | `InputType` |
| composite kind | `InputType.is_complex` |
| settings schema | `SettingsSchema` |
| resolved schema | `ResolvedSettingsSchema` (nested parts are `ResolvedSchema`) |
| reference map | `ref_map` |
| schema document | the dictionary passed to `SettingsSchema.from_spec` |
| backend | a subclass of `SettingsWizardBackend` |
| wizard | the form a backend renders, for Streamlit `StreamlitSettingsWizard` |
| submit function | the `submit_fn` argument of `render_wizard` |
