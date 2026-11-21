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

1. `fix-streamlit-collections`: make the rows of list, set, tuple and dict fields first-class, with stable ids instead of positions, so that removing a row no longer loses the remaining value and set and dict rows survive a duplicate error; show item defaults and `Item #n` labels, apply dict key renames (known issues 4 and 5), make `Remove` respect `minItems` and `Clear Items` respect read-only (known issues 6 and 7), and make dict limits follow `minProperties` and `maxProperties`. Remove the three matching inline `# ty: ignore` comments in `streamlit.py` (the optional `items`, `prefixItems` and `additionalProperties`).
2. `fix-streamlit-wizard-submission`: make `render_wizard` work for schemas with list, set, tuple, dict and additional-properties fields, which raise `st.button() can't be used in an st.form()` today (known issue 3). Choose in the explore between rendering collection schemas without a form and adding a `Save` button, and form-compatible controls that keep batched submission.
3. `fix-streamlit-object-defaults`: apply an object's default to its fields, so that a nested model default and a discriminated union default fill the fields that are shown; today `db: Db = Db(host="example.org")` shows empty fields and a union default preselects its alternative but does not prefill it.
4. `fix-schema-edge-cases`: classify date, time, datetime, duration and path formats, treat a single-value `Literal` as fixed, and resolve schema documents that have no `$defs` (known issues 1, 2 and 9).
5. `adopt-table-driven-tests`: use parametrized tables for the tests whose cases differ only by data, as `tests/test_mapper.py` and `tests/test_utils.py` already do (7 of 7 tests) and the backend tests do not (1 of 37): the scalar-field scenarios of the Streamlit backend (enum, boolean, number, text, validation) and the title-case cases in `tests/backends/test_base.py`, with each case id naming its spec scenario. Keep the click-and-rerun collection scenarios as single tests. Before committing to it, compare it with the other approaches in the explore: Hypothesis for the pure helpers in `utils.py`, and mutation testing (mutmut) to measure assertion strength, which the coverage figure does not.
6. `raise-coverage-to-90`: raise `fail_under` from 84 to 90 once the three Streamlit fixes and `fix-schema-edge-cases` have landed, because about 27 of the uncovered lines of `streamlit.py` are the date and time widgets that the mapper cannot reach until known issue 1 is fixed, and most of the rest sit in the collection paths those fixes rewrite. Add the missing tests with each fix, then raise the floor in a pull request.

## Later

- `redesign-resolved-schema`: make `ResolvedSchema` stop narrowing inherited mutable fields, so the scoped ty override for `config_wizard/schema.py` (19 diagnostics) can be removed.
- `add-exporter`: write the collected configuration to YAML, JSON and `.env`.
- `add-final-validation`: validate the result against the original model before export, and enforce required fields (known issue 8).
- `add-cli`: a `config-wizard` command that loads a class reference or a schema document and runs a backend (known issue 10).
- `add-typer-backend` and `add-textual-backend`: the two empty backend modules.
- `add-session-save-load`: save and load partial sessions.
- `add-plugin-system`: plugins for backends and serializers.
- `lint-pull-request-titles`: check in CI that a pull request title is one gitmoji-prefixed subject line, since the squash commit takes the title.
- `add-release-workflow`: build with `uv build` and publish to PyPI through trusted publishing once a first release is decided; the package is not on PyPI yet.
- `add-documentation-site`: build and publish the documentation; the `docs` extra and an empty `docs/` directory exist, but the generator is still to be chosen.
- `test-other-platforms`: add Windows and macOS runners to the CI matrix once a feature depends on file paths or terminal behavior, such as the command line or the Textual backend.
- `migrate-to-prek`: replace pre-commit with prek, a Rust reimplementation that reads the same `.pre-commit-config.yaml` and uses uv for Python environments, in the Makefile, devcontainer, CI and Dependabot configuration; first check that every hook in use works under it.
