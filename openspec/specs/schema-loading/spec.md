# schema-loading Specification

## Purpose

Turns a user's configuration definition, either a Python type or a JSON Schema / OpenAPI schema document, into a settings schema the wizard can render, keeping its reusable definitions available for reference resolution.

## Requirements

### Requirement: Load from a Pydantic model
The system SHALL build a settings schema from a Pydantic model class using the model's generated JSON Schema, exposing each model field as a schema property.

#### Scenario: Model fields become properties
- **WHEN** a Pydantic model with fields `name: str` and `age: int` is loaded
- **THEN** the settings schema has properties `name` and `age`

### Requirement: Load from a dataclass or TypedDict
The system SHALL build a settings schema from a standard-library dataclass or a TypedDict, exposing each field as a schema property.

#### Scenario: Dataclass fields become properties
- **WHEN** a dataclass with fields `name: str` and `age: int` is loaded
- **THEN** the settings schema has properties `name` and `age`

#### Scenario: TypedDict keys become properties
- **WHEN** a TypedDict with keys `name: str` and `age: int` is loaded
- **THEN** the settings schema has properties `name` and `age`

### Requirement: Reject unsupported Python types
The system SHALL reject a Python type that is not a Pydantic model, dataclass or TypedDict with a type error.

#### Scenario: Plain class is rejected
- **WHEN** a plain Python class that is none of the supported kinds is loaded
- **THEN** loading fails with a type error

### Requirement: Capture definitions from Python types
When loading from a Python type, the system SHALL keep the type's reusable definitions (`$defs`) as the schema's reference map, using an empty map when the type has none.

#### Scenario: Nested model definitions are kept
- **WHEN** a Pydantic model containing a nested Pydantic model is loaded
- **THEN** the reference map contains the nested model's definition

#### Scenario: Flat type yields an empty map
- **WHEN** a Pydantic model with only primitive fields is loaded
- **THEN** the reference map is an empty mapping

### Requirement: Load from a schema document
The system SHALL build a settings schema from a JSON Schema or OpenAPI 3.1 schema dictionary, validating it against the OpenAPI schema object model.

#### Scenario: Valid schema document
- **WHEN** a dictionary with `type: object` and properties `name` (string) and `age` (integer) is loaded
- **THEN** the settings schema has properties `name` and `age`

#### Scenario: Invalid schema document
- **WHEN** a dictionary declaring a property with the unknown type `float` is loaded
- **THEN** loading fails with a validation error

### Requirement: Capture definitions from schema documents
When loading from a schema dictionary, the system SHALL use its top-level `$defs` as the reference map if present, and SHALL leave the reference map unset otherwise.

#### Scenario: Document with definitions
- **WHEN** a schema dictionary with a top-level `$defs` entry `NestedSchema` is loaded
- **THEN** the reference map contains `NestedSchema`

#### Scenario: Document without definitions
- **WHEN** a schema dictionary with no `$defs` key is loaded
- **THEN** the reference map is unset

### Requirement: Replaceable reference map
The system SHALL allow the reference map to be replaced with a mapping or cleared, and SHALL reject any other value with a type error.

#### Scenario: Setting a mapping
- **WHEN** the reference map is set to `{"example": {"type": "string"}}`
- **THEN** reading it returns that mapping

#### Scenario: Setting a non-mapping
- **WHEN** the reference map is set to a string
- **THEN** the assignment fails with a type error
