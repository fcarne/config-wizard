# Spec Delta

## Purpose

Classifies each schema property into a single input kind so that every backend picks widgets from the same, backend-independent decision, and can tell simple inputs from composite ones.

## ADDED Requirements

### Requirement: Input kind vocabulary
The system SHALL define these input kinds: text, email, password, uri, uuid, file path, directory path, ipv4, ipv6, integer, float, date, time, datetime, duration, boolean, enum, list, tuple, set, dict, object, union, discriminated union, any and null.

#### Scenario: Vocabulary is closed
- **WHEN** a backend enumerates the available input kinds
- **THEN** it receives exactly the kinds listed above

### Requirement: Composite kinds
The system SHALL report list, tuple, set, dict, object, union and discriminated union as composite kinds, and every other kind as non-composite.

#### Scenario: Collection is composite
- **WHEN** the list kind is queried for being composite
- **THEN** the answer is true

#### Scenario: Scalar is not composite
- **WHEN** the text, any, null or enum kind is queried for being composite
- **THEN** the answer is false

### Requirement: Classification precedence
The system SHALL classify a property in this order: enum if it declares `enum` values; otherwise discriminated union if it declares a `discriminator`; otherwise union if it declares `anyOf` or `oneOf`; otherwise by its `type`. `allOf` is not considered.

#### Scenario: Enum wins over type
- **WHEN** a property has `type: string` and `enum: ["a", "b"]`
- **THEN** it is classified as enum

#### Scenario: Discriminator wins over plain union
- **WHEN** a property has `oneOf` alternatives and a `discriminator`
- **THEN** it is classified as discriminated union

#### Scenario: Optional value is a union
- **WHEN** a property is `anyOf` integer and null
- **THEN** it is classified as union

### Requirement: String classification by format
The system SHALL classify `type: string` as email, password, uri, uuid, ipv4 or ipv6 when `format` has that exact value, and as text for any other or missing format.

#### Scenario: Known format
- **WHEN** a property has `type: string` and `format: email`
- **THEN** it is classified as email

#### Scenario: Date, time and path formats fall back to text
- **WHEN** a property has `type: string` and `format` is `date`, `date-time`, `time`, `duration` or `path`
- **THEN** it is classified as text

#### Scenario: Single constant value is text
- **WHEN** a property has `type: string` and `const: "only"` with no `enum`
- **THEN** it is classified as text

### Requirement: Numeric and boolean classification
The system SHALL classify `type: number` as float, `type: integer` as integer and `type: boolean` as boolean.

#### Scenario: Number
- **WHEN** a property has `type: number`
- **THEN** it is classified as float

### Requirement: Array classification
The system SHALL classify `type: array` as tuple when it declares `prefixItems`, otherwise as set when `uniqueItems` is true, otherwise as list.

#### Scenario: Fixed-position items
- **WHEN** an array property declares `prefixItems`
- **THEN** it is classified as tuple

#### Scenario: Unique items
- **WHEN** an array property declares `uniqueItems: true` and no `prefixItems`
- **THEN** it is classified as set

### Requirement: Object classification
The system SHALL classify `type: object` as object when it declares non-empty `properties`, otherwise as dict when it declares truthy `additionalProperties`, otherwise as any.

#### Scenario: Named fields
- **WHEN** an object property declares `properties`
- **THEN** it is classified as object

#### Scenario: Free-form mapping
- **WHEN** an object property declares no `properties` and `additionalProperties` is a schema
- **THEN** it is classified as dict

#### Scenario: Unconstrained object
- **WHEN** an object property declares neither `properties` nor `additionalProperties`
- **THEN** it is classified as any

### Requirement: Null and unknown types
The system SHALL classify `type: null` as null and any other or missing type as any.

#### Scenario: Null type
- **WHEN** a property has `type: null`
- **THEN** it is classified as null
