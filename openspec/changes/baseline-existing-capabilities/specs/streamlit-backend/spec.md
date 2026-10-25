# Spec Delta

## Purpose

Renders a settings schema as an interactive Streamlit form, choosing a widget for each input kind, applying schema constraints in the UI, and returning the user's configuration on save.

## ADDED Requirements

### Requirement: Isolated wizard state
The Streamlit wizard SHALL keep its entered values in the Streamlit session under a key derived from the caller-supplied key, or else the schema title, or else the schema's type name in kebab case, so values persist across reruns and two wizards with different keys do not share values.

#### Scenario: Two wizards on one page
- **WHEN** two wizards with keys `a` and `b` are rendered on the same page
- **THEN** values entered in one do not appear in the other

### Requirement: Form layout and submission
For schemas without sequence, dict or additional-properties fields, the Streamlit wizard SHALL render inside a form showing the schema title as a subheader (unless disabled) and the description, with a submit button labelled `Save` by default, clearing the form on submit unless disabled.

#### Scenario: Default form
- **WHEN** a wizard for a schema titled `AppSettings` with only scalar fields is rendered with default options
- **THEN** the form shows `AppSettings` as a subheader and a `Save` button

### Requirement: Formless rendering
The Streamlit wizard SHALL support rendering the schema directly into the page without a form, returning the current values on every rerun. This is the mode that supports sequence, dict and additional-properties fields.

#### Scenario: Live values
- **WHEN** the schema is rendered without a form and the user changes a field
- **THEN** the next rerun returns the updated value

### Requirement: Common field presentation
For every field widget, the Streamlit wizard SHALL use the property title as label, the description as help text (except for collection items), the schema `default` as initial value, the first of `examples` (or `example`) as placeholder, and SHALL disable the widget when the property is `readOnly`.

#### Scenario: Read-only default
- **WHEN** a string property has `default: "localhost"` and `readOnly: true`
- **THEN** a disabled text field showing `localhost` is rendered

### Requirement: Enum fields
The Streamlit wizard SHALL render an enum property as a dropdown of its values with the default preselected, and SHALL return the only value without rendering a widget when exactly one value is allowed.

#### Scenario: Several options
- **WHEN** an enum property allows `option_a`, `option_b`, `option_c` with default `option_b`
- **THEN** a dropdown with the three values is shown with `option_b` selected

#### Scenario: Single option
- **WHEN** an enum property allows only `A`
- **THEN** no widget is shown and the value `A` is returned

### Requirement: Boolean fields
The Streamlit wizard SHALL render a boolean property as a toggle.

#### Scenario: Toggle
- **WHEN** a boolean property with `default: false` is rendered
- **THEN** a toggle in the off position is shown

### Requirement: Numeric fields
The Streamlit wizard SHALL render integers with step 1 and floats with step 0.01, using `multipleOf` as step when given. Bounds come from `minimum`/`maximum`, or from `exclusiveMinimum`/`exclusiveMaximum` moved inward by one step. With both bounds a slider is shown, otherwise a number field.

#### Scenario: Bounded integer
- **WHEN** an integer property has `minimum: 1` and `maximum: 10`
- **THEN** a slider from 1 to 10 with step 1 is shown

#### Scenario: Exclusive bound
- **WHEN** an integer property has `exclusiveMinimum: 0` and no maximum
- **THEN** a number field with minimum 1 is shown

### Requirement: Text fields
The Streamlit wizard SHALL render text-like properties as a single-line text field limited to `maxLength` characters when given, masking input for the password kind.

#### Scenario: Password
- **WHEN** a string property with `format: password` is rendered
- **THEN** a masked text field is shown

### Requirement: Inline format validation
The Streamlit wizard SHALL check a text value against the property's `pattern`, or against a built-in pattern for email, uuid, uri, ipv4 and ipv6, show an error beside the field when a non-empty value does not match, and still return the entered value.

#### Scenario: Invalid email
- **WHEN** the user types `not-an-email` into an email property
- **THEN** the message `Please enter a valid email address.` is shown beside the field and `not-an-email` is returned

#### Scenario: Custom pattern
- **WHEN** a property has `pattern: "^[a-z]+$"` and the user types `ABC`
- **THEN** an error naming the expected pattern is shown beside the field

### Requirement: Sequence fields
The Streamlit wizard SHALL render list, tuple and set properties as a titled section of item rows with `Add Item` and per-row `Remove` buttons. The row count starts from the stored value, else the default, else `minItems`. It SHALL return a list, tuple or set respectively.

#### Scenario: Adding an item
- **WHEN** the user presses `Add Item` on a list with one row
- **THEN** a second, empty row is shown

#### Scenario: Tuple items by position
- **WHEN** a tuple property declares `prefixItems` integer then string
- **THEN** the first row is a number field and the second a text field, and a tuple is returned

### Requirement: Sequence size limits
The Streamlit wizard SHALL disable `Add Item` on a sequence or dict when its entry count reaches `maxItems` or the property is read-only.

#### Scenario: Maximum reached
- **WHEN** a list with `maxItems: 2` has two rows
- **THEN** its `Add Item` button is disabled

### Requirement: Set uniqueness feedback
The Streamlit wizard SHALL show an error when a set property contains duplicate entries and return the de-duplicated set.

#### Scenario: Duplicate entries
- **WHEN** the user enters `1` and `1` in a set of integers
- **THEN** a duplicate-items error is shown and `{1}` is returned

### Requirement: Dictionary fields
The Streamlit wizard SHALL render a dict property as rows of key text field and value widget, with the value kind taken from `additionalProperties` (any kind when it is `true`). Rows start from the stored value, else the default, else empty, with values prefilled. `Add Item` adds a row with the next free key `new_item_<n>`.

#### Scenario: New row key
- **WHEN** the user presses `Add Item` on a dict with keys `new_item_0` and `new_item_1`
- **THEN** a row with key `new_item_2` is added

#### Scenario: Default entries
- **WHEN** a dict of integers with default `{"a": 1, "b": 2}` is rendered
- **THEN** two rows `a`=1 and `b`=2 are shown and `{"a": 1, "b": 2}` is returned

### Requirement: Object fields
The Streamlit wizard SHALL render an object property as a titled group containing each of its properties in declaration order, followed by an additional-properties section when the object allows them.

#### Scenario: Nested group
- **WHEN** an object property `db` with fields `host` and `port` is rendered
- **THEN** a `Db` heading followed by `Host` and `Port` fields is shown

### Requirement: Union fields
The Streamlit wizard SHALL render a union as a selector of its alternatives, labelled by alternative title or else type and format, and render the selected alternative below. A default preselects the alternative whose discriminator value matches it, or for plain unions the first alternative the default validates against.

#### Scenario: Discriminated default
- **WHEN** a discriminated union on `type` has default `{"type": "B", ...}`
- **THEN** the alternative whose `type` is `B` is preselected and prefilled

#### Scenario: Optional integer
- **WHEN** a property is `anyOf` integer and null
- **THEN** a selector offers `integer` and `null`

### Requirement: Free-form fields
The Streamlit wizard SHALL render an any-kind property as a multi-line text area whose content is parsed as JSON, and SHALL show an invalid-JSON error and return the raw text when parsing fails.

#### Scenario: Valid JSON
- **WHEN** the user enters `{"a": 1}`
- **THEN** the mapping `{"a": 1}` is returned

#### Scenario: Invalid JSON
- **WHEN** the user enters `{a: 1}`
- **THEN** an invalid-JSON error is shown and the text `{a: 1}` is returned

### Requirement: Null fields
The Streamlit wizard SHALL render nothing for a null-kind property and return no value for it.

#### Scenario: Null alternative selected
- **WHEN** the `null` alternative of an optional property is selected
- **THEN** no input is shown and the property's value is null
