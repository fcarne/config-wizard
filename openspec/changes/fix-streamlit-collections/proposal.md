# Proposal

## Why

The Streamlit backend renders collection fields but the collection handling defects found while baselining (`fix-streamlit-collections` known issues 3 to 7) make the wizard produce invalid or lossy values: removing a middle row drops the remaining values, renaming a dict key is ignored, sequence item defaults are never shown, and the add/clear/remove button state logic does not follow the schema limits.

## What Changes

- Make the rows of list, set, tuple and dict fields stable: removing a row keeps the remaining values of the sequence, and the duplicate check de-duplicates and keeps a single entry for sets.
- Show sequence item defaults: a default such as `[5]` renders one prefilled row and returns `[5]`.
- Show item labels as `Item #n` and apply them to the row widgets.
- Apply dict key renames: renaming a key to a new name renames the row, and renaming onto an existing key overwrites that row instead of losing the renamed one.
- Make `Remove` respect `minItems` and `Clear Items` respect `readOnly` (currently both checks are inverted).
- Make dict limits follow `minProperties` and `maxProperties`, and set `Add Item` limits from the same counts.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `streamlit-backend`: the "Sequence fields", "Sequence size limits", "Set uniqueness feedback", "Dictionary fields" and "Form layout and submission" requirements are corrected or refined to what the wizard must do when it renders collections.

## Impact

- Modified: `config_wizard/backends/streamlit.py` (`_render_list_input`, `_render_list_item_input`, `_render_dict_input`, `_render_dict_items`, `_render_dict_item_input`, `_is_add_button_disabled`, `_is_clear_button_disabled`, `_is_remove_button_disabled`).
- Added: tests in `tests/backends/test_streamlit.py` for every collection scenario.
- Unchanged: schema resolution, mapper input kinds, the backend contract, the export/validation layers (not implemented yet).

## Out of Scope

- Rendering collection schemas without a form, which is a separate roadmap item (`fix-streamlit-wizard-submission`).
- Object default application, which is a separate roadmap item (`fix-streamlit-object-defaults`).
- Date, time, duration and path widgets, which are a separate roadmap item (`fix-schema-edge-cases`).
- Required-field enforcement, which is a separate roadmap item (known issue 8).
