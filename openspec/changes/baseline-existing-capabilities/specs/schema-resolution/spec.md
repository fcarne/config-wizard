# Spec Delta

## Purpose

Produces a self-contained settings schema by inlining every `$ref` from a reference map, so that backends can walk the schema without following references themselves.

## ADDED Requirements

### Requirement: Inline references
The system SHALL replace every `$ref` object in the schema, at any depth, with the referenced definition from the reference map, resolving references inside inlined definitions as well. The definition is looked up by the last path segment of the `$ref` value.

#### Scenario: Nested model reference is inlined
- **WHEN** a schema whose property `nested` is `{"$ref": "#/$defs/NestedSchema"}` is resolved with a reference map containing `NestedSchema`
- **THEN** the resolved property `nested` is the `NestedSchema` object definition, with its own properties and required list

### Requirement: Explicit reference map
The system SHALL resolve against an explicitly supplied reference map when one is given, and against the schema's own reference map otherwise.

#### Scenario: Map supplied by the caller
- **WHEN** a schema document loaded without `$defs` is resolved with the definitions passed explicitly
- **THEN** resolution succeeds and references are inlined from the supplied map

### Requirement: Fail without a reference map
The system SHALL fail with a value error when neither an explicit nor an own reference map is available, regardless of whether the schema contains references.

#### Scenario: No map available
- **WHEN** a schema loaded from a document without `$defs` is resolved with no map supplied
- **THEN** resolution fails with a value error stating that no reference map was provided

### Requirement: Fail on unknown references
The system SHALL fail with a key error naming the missing definition when a `$ref` points to a definition absent from the reference map.

#### Scenario: Missing definition
- **WHEN** a schema references `NonExistentSchema` and the reference map lacks it
- **THEN** resolution fails with a key error whose message names `NonExistentSchema`

### Requirement: Fail on circular references
The system SHALL fail with a value error when inlining does not terminate because a definition references itself directly or indirectly.

#### Scenario: Self-referencing model
- **WHEN** a model with a field typed as an optional instance of itself is resolved
- **THEN** resolution fails with a value error stating that a circular reference was detected

### Requirement: Untyped subschemas default to object
In a resolved schema, the system SHALL treat any subschema that declares no `type` as type `object`.

#### Scenario: Unconstrained field
- **WHEN** a model with a field typed `Any` is resolved
- **THEN** that property's type is `object` and it declares no properties
