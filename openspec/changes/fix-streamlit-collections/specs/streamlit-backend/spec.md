# Spec Delta

## MODIFIED Requirements

### Requirement: Sequence fields

The Streamlit wizard SHALL render list, tuple and set properties as sections of item rows with `Add Item` and per-row `Remove` buttons, keeping a stable row identity so removing one row does not lose the values of the remaining rows.

#### Scenario: Adding an item
- **WHEN** the user presses `Add Item` on a list with one row
- **THEN** a second, empty row is shown

#### Scenario: Tuple items by position
- **WHEN** a tuple property declares `prefixItems` integer then string
- **THEN** the first row is a number field and the second a text field, and a tuple is returned

#### Scenario: Stable rows after removal
- **WHEN** a list shows rows `A`, `B`, `C` and the user removes the first row
- **THEN** rows `B` and `C` remain in order and the wizard returns `["B", "C"]`

#### Scenario: Removing a middle row keeps its neighbours
- **WHEN** a list shows rows `A`, `B`, `C` and the user removes row `B`
- **THEN** rows `A` and `C` remain and the wizard returns `["A", "C"]`

#### Scenario: Item defaults shown
- **WHEN** an array property of strings has `default: ["a", "b"]`
- **THEN** two rows show `a` and `b` and the wizard returns `["a", "b"]`

#### Scenario: Tuple item defaults
- **WHEN** a tuple of integer then string has `default: [3, "x"]`
- **THEN** the number row shows `3` and the text row shows `x`, and a tuple `(3, "x")` is returned

#### Scenario: Item labels
- **WHEN** a list row is rendered
- **THEN** its label reads `Item #1`, `Item #2`, etc., and not its internal key

### Requirement: Sequence size limits

The Streamlit wizard SHALL disable `Add Item` on a sequence or dict when its entry count reaches `maxItems` or the property is read-only, and SHALL disable per-row `Remove` when the entry count is at `minItems`. `Clear Items` SHALL be enabled for editable fields and disabled for read-only fields.

#### Scenario: Maximum reached
- **WHEN** a list with `maxItems: 2` has two rows
- **THEN** its `Add Item` button is disabled

#### Scenario: Remove disabled at minimum
- **WHEN** a list with `minItems: 1` has one row
- **THEN** its `Remove` button is disabled

#### Scenario: Clear Items enabled for editable fields
- **WHEN** an editable list has one row
- **THEN** its `Clear Items` button is enabled

#### Scenario: Clear Items disabled for read-only fields
- **WHEN** a read-only list has one row
- **THEN** its `Clear Items` button is disabled

### Requirement: Set uniqueness feedback

The Streamlit wizard SHALL show an error when a set property contains duplicate entries and return the de-duplicated set.

#### Scenario: Duplicate entries
- **WHEN** the user enters `1` and `1` in a set of integers
- **THEN** a duplicate-items error is shown and `{1}` is returned

#### Scenario: Duplicate entries kept across rerun
- **WHEN** the user enters `1` and `1` in a set of integers and reruns
- **THEN** both rows remain, a duplicate-items error is shown, and `{1}` is returned

### Requirement: Dictionary fields

The Streamlit wizard SHALL render a dict property as rows of key text field and value widget, with the value kind taken from `additionalProperties` (any kind when it is `true`). Rows start from the stored value, else the default, else empty, with values prefilled.

#### Scenario: New row key
- **WHEN** the user presses `Add Item` on a dict with keys `new_item_0` and `new_item_1`
- **THEN** a row with key `new_item_2` is added

#### Scenario: Default entries
- **WHEN** a dict of integers with default `{"a": 1, "b": 2}` is rendered
- **THEN** two rows `a`=1 and `b`=2 are shown and `{"a": 1, "b": 2}` is returned

#### Scenario: Key rename keeps its row
- **WHEN** a dict shows rows `a`=1, `b`=2 and the user renames key `b` to `c`
- **THEN** rows `a`=1, `c`=2 are shown and `{"a": 1, "c": 2}` is returned

#### Scenario: Renaming onto an existing key overwrites it
- **WHEN** a dict shows rows `a`=1, `b`=2 and the user renames key `b` to `a`
- **THEN** row `a` holds `2`, one row remains, and `{"a": 2}` is returned

## ADDED Requirements

### Requirement: Dict size limits

The Streamlit wizard SHALL disable `Add Item` on a dict when its entry count reaches `maxProperties` or the property is read-only, and SHALL disable per-row `Remove` when the entry count is at `minProperties`.

#### Scenario: Add Item disabled at maximum properties
- **WHEN** a dict with `maxProperties: 2` has two rows
- **THEN** its `Add Item` button is disabled

#### Scenario: Remove disabled at minimum properties
- **WHEN** a dict with `minProperties: 1` has one row
- **THEN** its `Remove` button is disabled
