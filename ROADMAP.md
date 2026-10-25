# Roadmap

Ordered backlog of what is not done yet. This is not a spec: requirements and design live in the OpenSpec change that implements an item.

How it is used: pick the next item and run `/opsx:explore <item>`. When its change is archived, delete the item here in the same pull request. Nothing listed here is implemented; do not describe it as available.

Known issue numbers refer to the table in the design of the archived `baseline-existing-capabilities` change.

## Adding an item

- Write it as `` `change-name`: what and why ``, adding the known issue numbers it covers when it fixes any.
- Check it is not already covered by a spec in `openspec/specs/` or a change in `openspec/changes/`.
- Place it by dependency. Do not reorder existing items without asking.
- Leave requirements and design out. They belong to the change that implements the item.

## Next

1. `migrate-to-ty`: replace mypy with ty in pre-commit, the dev group, the Makefile, `AGENTS.md`, `CONSTITUTION.md` and `.claude/settings.json`. ty 0.0.91 is beta; a trial run reported 35 diagnostics in `config_wizard/` (19 field overrides in `schema.py`, 16 Streamlit calls) where mypy reports none, and ty has no equivalent of the Pydantic mypy plugin, project mypy 2.4.0 with real Streamlit types also reports 11 errors (7 `call-overload`) and `jsonschema` has no stubs in the project environment, so triage the diagnostics before switching.
2. `add-ci-pipeline`: run lint, mypy, tests and `openspec validate --all --strict` on every pull request, with a pull request template that links the OpenSpec change (known issue 12).
3. `test-streamlit-backend`: an automated Streamlit test suite using Streamlit's `AppTest`, covering the scenarios in the `streamlit-backend` spec, and a tracked, working manual harness or its removal (known issues 11 and 13).
4. `fix-streamlit-collections`: make `render_wizard` work for list, set, tuple, dict and additional-properties fields, and fix dict key renames, list defaults, `minItems` on remove and the clear button (known issues 3 to 7).
5. `fix-schema-edge-cases`: classify date, time, datetime, duration and path formats, treat a single-value `Literal` as fixed, and resolve schema documents that have no `$defs` (known issues 1, 2 and 9).

## Later

- `add-exporter`: write the collected configuration to YAML, JSON and `.env`.
- `add-final-validation`: validate the result against the original model before export, and enforce required fields (known issue 8).
- `add-cli`: a `config-wizard` command that loads a class reference or a schema document and runs a backend (known issue 10).
- `add-typer-backend` and `add-textual-backend`: the two empty backend modules.
- `add-session-save-load`: save and load partial sessions.
- `add-plugin-system`: plugins for backends and serializers.
