# Design

## Context

The Streamlit backend renders collections by index: a list row `i` is addressed as `<property_key>.<i>`, its widget key is `<run_id>-<wizard key>-<property_key>.<i>` and its output is a list built in index order. That was adequate while rows could only be appended. Once rows can be removed, the addressing is wrong: removing row 1 renumbers the remaining rows, so their widget state moves under keys that no longer match their identity.

Evidence from scratch `AppTest` runs on the current code (Streamlit 1.66.1, Python 3.11, commit on `main`):

| # | Finding | Evidence |
|---|---------|----------|
| 4 | Renaming a dict key to a new name is ignored | `{"a":1,"b":2}`, rename `b` to `c` returns `{"a":1,"b":2}`; rename `b` to `a` returns `{"a":2}` |
| 5 | Sequence item defaults are not shown | `default: [5]` renders one empty row and returns `[None]`; an object item default `{"a":"x","b":1}` renders empty fields; a tuple default `[3, "x"]` renders `(None, None)` |
| 6 | `Remove` ignores `minItems` | A list with `minItems: 1` and one row has `Remove` enabled |
| 7 | `Clear Items` is inverted | Editable list: `Clear Items` disabled; read-only list: `Clear Items` enabled |

The roadmap adds to those known issues the requirements that the collection rows be first-class and survive removal, and that set and dict rows survive duplicate and rename errors.

## Goals / Non-Goals

**Goals:**

- Rows of list, set, tuple and dict fields keep stable identities, so removing a row keeps the remaining values.
- Sequence item defaults are shown, and rows are labelled `Item #n`.
- Dict key renames move the value; renaming onto an existing key overwrites that row.
- `Remove` respects the minimum, `Clear Items` respects read-only, `Add Item` respects the maximum.
- Dict limits follow `minProperties` and `maxProperties`.

**Non-Goals:**

- Rendering collection schemas without a form (`fix-streamlit-wizard-submission`).
- Applying object defaults to nested fields (`fix-streamlit-object-defaults`).
- Date, time, duration and path widgets (`fix-schema-edge-cases`).
- Required-field enforcement (known issue 8).

## Decisions

### Row identity: stable ids for sequences, keys for dicts

Sequences and sets keep an ordered list of opaque row ids in the wizard state, allocated from a monotonic counter per property. Dict rows keep the user key as identity, so a rename is a move of the value.

- **Sequences/sets**: each row is addressed by its id (the widget key carries the id, not the index). Adding appends a new id; removing drops the id together with its value; clearing re-allocates for the minimum.
- **Dicts**: identity is the key. Renaming writes the value to the new key and drops the old one; renaming onto an occupied key overwrites that row.

Alternatives considered:

- *Keep positional keys and shift state on removal* (rejected: it is the observed defect; it fails as soon as a user removes a row before editing the others).
- *Derive ids from the values* (rejected: sets are de-duplicated and values can repeat, and objects change value per keystroke).

### Where row ids live

Ids are stored in the wizard's session-state namespace under a backend-reserved key (per wizard key), a sibling of the value state, never as part of the returned data. Missing ids are allocated lazily from the stored value or the default, so a fresh wizard shows the default rows with their defaults.

### Set duplicates survive the rerun

The returned value of a set is the de-duplicated set, but the row state is kept raw for the rerun, so the user sees the duplicate error and can correct the values; the de-duplicated set is returned.

### Button disabling

`_is_add_button_disabled`, `_is_clear_button_disabled` and `_is_remove_button_disabled` take the count of entries and the property schema. `Add Item` is disabled at `maxItems`/`maxProperties` or when read-only; `Remove` is disabled at `minItems`/`minProperties`; `Clear Items` is disabled only when read-only.

### Item defaults and labels

`_render_list_item_input` deep-copies the item schema and seeds its default from the current row value, so a default such as `[5]` renders one prefilled row; the label is `Item #n` with n starting at 1.

### Dict size limits

Dicts use `minProperties`/`maxProperties` in place of the sequence counts, so `Add Item` and `Remove` follow the property limits.

## Risks / Trade-offs

- [Widget keys shared across wizards] -> Row ids are namespaced by the wizard key; the run id prefixes widget keys.
- [Tuple arity semantics] -> Tuples keep prefix-position addressing for the item schemas; add/remove on fixed-arity tuples stays out of scope of the spec scenarios.

## Migration Plan

No data migration: wizard state is per session and per wizard key.

## Open Questions

None.
