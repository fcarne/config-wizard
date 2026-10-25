# Spec Delta

## Purpose

Defines the behavior every interactive wizard backend shares, independent of the UI toolkit: how it prepares the schema, walks its properties, labels them, collects values and returns the user's configuration.

## ADDED Requirements

### Requirement: Resolve schema on construction
A backend SHALL resolve references in the given settings schema when it is created, using the schema's own reference map, and SHALL use an already-resolved schema as is.

#### Scenario: Unresolved schema
- **WHEN** a backend is created from a schema loaded from a Pydantic model with a nested model
- **THEN** the backend works on a schema in which the nested model is inlined

#### Scenario: Unresolvable schema
- **WHEN** a backend is created from a schema document loaded without `$defs`
- **THEN** creation fails with the resolution error for a missing reference map

### Requirement: Render properties in declaration order
A backend SHALL render each top-level property once, in the order the schema declares them, telling the renderer whether the property is listed in the schema's `required`.

#### Scenario: Required flag
- **WHEN** a schema declares properties `a` and `b` with `required: ["a"]`
- **THEN** `a` is rendered as required and `b` as not required, `a` before `b`

### Requirement: Default property titles
A backend SHALL label a property that has no `title` with its key converted to title case, splitting on camelCase boundaries, underscores, hyphens and spaces.

#### Scenario: Snake case key
- **WHEN** a property with key `max_retry_count` and no title is rendered
- **THEN** its label is `Max Retry Count`

#### Scenario: Camel case key
- **WHEN** a property with key `maxRetryCount` and no title is rendered
- **THEN** its label is `Max Retry Count`

### Requirement: Empty schema yields empty output
A backend SHALL return an empty mapping without rendering anything when the schema declares no properties.

#### Scenario: No properties
- **WHEN** a schema with no `properties` is rendered
- **THEN** the output is `{}`

### Requirement: Additional properties
When the top-level schema allows additional properties, a backend SHALL let the user enter free key/value pairs after the declared properties, and SHALL merge those pairs into the output at the same level as the declared properties.

#### Scenario: Extra key entered
- **WHEN** a schema with property `name` and `additionalProperties: true` is rendered and the additional-properties entries hold `extra: 1`
- **THEN** the output contains both `name` and `extra: 1` at the top level

#### Scenario: Nested additional properties are flattened
- **WHEN** a nested object allowing additional properties has the additional entry `k`
- **THEN** `k` appears directly inside that nested object in the output

### Requirement: Output shape
A backend SHALL return the collected values as a mapping keyed by property name, with nested objects as nested mappings.

#### Scenario: Nested object value
- **WHEN** a schema with an object property `db` having fields `host` and `port` is filled in
- **THEN** the output contains `db` as a mapping with keys `host` and `port`

### Requirement: Wizard submission
A backend SHALL present the rendered schema as a wizard with a submit action, SHALL return nothing until the user submits, and on submit SHALL pass the collected output, plus any extra arguments the caller supplied, to the caller's submit function and return its result. Without a submit function, the collected output itself is returned.

#### Scenario: Not yet submitted
- **WHEN** the wizard is displayed and the user has not submitted
- **THEN** the wizard returns nothing

#### Scenario: Submitted with a submit function
- **WHEN** the user submits and the caller supplied a submit function that writes a file and returns its path
- **THEN** the wizard returns that path

### Requirement: User-facing messages
A backend SHALL provide warning and error messages with an optional title, shown as `**title**:` followed by the message, and SHALL show nothing when the message is empty.

#### Scenario: Titled warning
- **WHEN** a warning with title `Heads up` and message `Port in use` is shown
- **THEN** the user sees the title in bold followed by the message

#### Scenario: Empty message
- **WHEN** an error with an empty message is shown
- **THEN** nothing is displayed
