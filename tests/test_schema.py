import pytest
from openapi_pydantic import DataType
from pydantic import ValidationError, BaseModel, TypeAdapter

from config_wizard.schema import SettingsSchema, ResolvedSettingsSchema


class NestedSchema(BaseModel):
    nested_property: str


class MainSchema(BaseModel):
    nested: NestedSchema


def test_from_spec__valid_openapi_spec__returns_schema(valid_openapi_spec: dict) -> None:
    """Test that a valid OpenAPI spec returns a SettingsSchema instance with expected properties."""
    spec = valid_openapi_spec

    schema = SettingsSchema.from_spec(spec)

    assert schema is not None
    assert schema.properties is not None
    assert "name" in schema.properties
    assert "age" in schema.properties

    assert schema.ref_map is None


def test_from_spec__valid_openapi_spec_with_refs__returns_schema_with_refs() -> None:
    """Test that a valid OpenAPI spec with references returns a SettingsSchema instance with expected properties."""

    spec = MainSchema.model_json_schema()

    schema = SettingsSchema.from_spec(spec)

    assert schema is not None
    assert schema.properties is not None
    assert "nested" in schema.properties

    assert schema.ref_map is not None
    assert "NestedSchema" in schema.ref_map


def test_from_spec__invalid_openapi_spec__raises_validation_error(
    invalid_openapi_spec,
) -> None:
    """Test that an invalid OpenAPI spec raises a ValidationError."""
    spec = invalid_openapi_spec

    with pytest.raises(ValidationError):
        SettingsSchema.from_spec(spec)


@pytest.mark.parametrize(
    "user_type",
    [
        "user_model",
        "user_dataclass",
        "user_typeddict",
    ],
)
def test_from_schema__valid_types__returns_schema(user_type, request: pytest.FixtureRequest) -> None:
    """Test that valid user types return a SettingsSchema instance with expected properties."""
    tp: type = request.getfixturevalue(user_type)
    schema = SettingsSchema.from_schema(tp)

    assert schema is not None
    assert schema.properties is not None
    assert "name" in schema.properties
    assert "age" in schema.properties

    if isinstance(tp, BaseModel):
        assert schema.ref_map == tp.model_json_schema().get("$defs", {})
    else:
        assert schema.ref_map == TypeAdapter(tp).json_schema().get("$defs", {})


def test_from_schema__with_invalid_class__raises_type_error(user_class) -> None:
    """Test that passing an invalid class to from_schema raises a TypeError."""
    cls = user_class

    with pytest.raises(TypeError):
        SettingsSchema.from_schema(cls)


def test_ref_map__set_and_get__correct_value() -> None:
    """Test that ref_map can be set and retrieved correctly."""
    schema = SettingsSchema()
    ref_map = {"example": {"type": "string"}}

    schema.ref_map = ref_map

    assert schema.ref_map == ref_map


def test_ref_map__set_invalid_type__raises_type_error() -> None:
    """Test that setting ref_map to an invalid type raises a TypeError."""
    schema = SettingsSchema()

    with pytest.raises(TypeError):
        schema.ref_map = "invalid_type"  # type: ignore[assignment] # Should be a dict or None


def test_resolve_ref__valid_ref__returns_correct_value() -> None:
    """Test that resolve_refs returns the correct value for a valid reference."""

    schema = SettingsSchema.from_schema(MainSchema)
    resolved_schema = schema.resolve_refs()

    assert isinstance(resolved_schema, ResolvedSettingsSchema)
    assert resolved_schema.model_dump(exclude_unset=True)["properties"] == {
        "nested": {
            "type": DataType.OBJECT,
            "properties": {"nested_property": {"title": "Nested Property", "type": DataType.STRING}},
            "required": ["nested_property"],
            "title": "NestedSchema",
        }
    }


def test_resolve_ref__pass_ref_map__returns_correct_value() -> None:
    """Test that resolve_refs returns the correct value when a ref_map is passed."""

    spec = MainSchema.model_json_schema()
    defs = spec.pop("$defs", {})

    schema = SettingsSchema.from_spec(spec)

    assert schema.ref_map is None  # Initially, ref_map should be None

    resolved_schema = schema.resolve_refs(ref_map=defs)

    assert isinstance(resolved_schema, ResolvedSettingsSchema)
    assert resolved_schema.model_dump(exclude_unset=True)["properties"] == {
        "nested": {
            "type": DataType.OBJECT,
            "properties": {"nested_property": {"title": "Nested Property", "type": DataType.STRING}},
            "required": ["nested_property"],
            "title": "NestedSchema",
        }
    }


def test_resolve_ref__invalid_ref__raises_value_error() -> None:
    """Test that resolve_refs raises a ValueError for an invalid reference."""

    class NonExistentSchema(BaseModel):
        non_existent: int

    class MainSchemaWithNonExistent(BaseModel):
        nested: NestedSchema
        invalid_ref: NonExistentSchema

    schema = SettingsSchema.from_schema(MainSchemaWithNonExistent)

    defs = MainSchemaWithNonExistent.model_json_schema().get("$defs", {})
    del defs["NonExistentSchema"]  # Simulate a missing reference

    schema.ref_map = defs  # Update the ref_map to simulate the missing reference

    with pytest.raises(KeyError, match="Reference 'NonExistentSchema' not found in ref_map"):
        schema.resolve_refs()


def test_resolve_ref__no_ref_map__raises_value_error() -> None:
    """Test that resolve_refs raises a ValueError when no ref_map is provided."""

    spec = MainSchema.model_json_schema()
    del spec["$defs"]  # Remove $defs to simulate no ref_map

    schema = SettingsSchema.from_spec(spec)

    # ValueError("No reference map provided for resolving references."
    with pytest.raises(ValueError, match="No reference map provided for resolving references."):
        schema.resolve_refs()


def test_resolve_ref__circular_ref__raises_value_error() -> None:
    """Test that resolve_refs raises a ValueError for circular references."""

    class CircularSchema(BaseModel):
        value: str
        self_ref: "CircularSchema | None" = None

    schema = SettingsSchema.from_schema(CircularSchema)
    with pytest.raises(ValueError, match="Circular reference detected"):
        schema.resolve_refs()
