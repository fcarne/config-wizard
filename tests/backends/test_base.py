from typing import Any

import pytest
from pydantic import BaseModel

from config_wizard.backends.base import ADDITIONAL_PROPERTIES_KEY, SettingsWizardBackend
from config_wizard.schema import ResolvedSchema, SettingsSchema


class RecordingBackend(SettingsWizardBackend):
    def __init__(
        self,
        schema: SettingsSchema,
        values: dict[str, Any] | None = None,
        additional_properties: dict[str, Any] | None = None,
    ) -> None:
        self.values = values or {}
        self.additional_properties = additional_properties or {}
        self.rendered: list[tuple[str, str | None, bool]] = []
        super().__init__(schema)

    def _init_state(self) -> dict[str, Any]:
        return {}

    def _store_value(self, key: str, value: Any) -> None:
        self.state[key] = value

    def _get_value(self, key: str) -> Any:
        return self.state.get(key)

    def _render_property(
        self, property_key: str, property_schema: ResolvedSchema, required: bool, is_item: bool, container: Any = None
    ) -> Any:
        self.rendered.append((property_key, property_schema.title, required))
        return self.values.get(property_key)

    def _render_additional_properties(
        self, key: str, property_schema: ResolvedSchema, is_item: bool, container: Any = None
    ) -> dict[str, Any]:
        return self.additional_properties

    def render_wizard(self, *args: Any, **kwargs: Any) -> None:
        return None

    def warning(self, *, title: str | None = None, message: str) -> None:
        return None

    def error(self, *, title: str | None = None, message: str) -> None:
        return None


class NestedModel(BaseModel):
    nested_property: str


class ParentModel(BaseModel):
    nested: NestedModel


def object_spec(properties: dict[str, Any], **extra: Any) -> dict[str, Any]:
    return {"type": "object", "$defs": {}, "properties": properties, **extra}


def test_init__unresolved_schema__inlines_nested_model() -> None:
    """Test that a backend created from a model with a nested model works on a schema with the model inlined."""
    backend = RecordingBackend(SettingsSchema.from_schema(ParentModel))

    assert backend.schema.properties is not None
    nested = backend.schema.properties["nested"]
    assert nested.properties is not None
    assert "nested_property" in nested.properties


def test_init__schema_without_defs__raises_missing_reference_map_error() -> None:
    """Test that creating a backend from a schema document loaded without `$defs` fails with the resolution error."""
    schema = SettingsSchema.from_spec({"type": "object", "properties": {"a": {"type": "string"}}})

    with pytest.raises(ValueError, match="No reference map provided"):
        RecordingBackend(schema)


def test_render_schema__required_property__renders_in_declaration_order_with_required_flag() -> None:
    """Test that properties are rendered once, in declaration order, flagged by the schema's `required`."""
    schema = SettingsSchema.from_spec(
        object_spec({"a": {"type": "string"}, "b": {"type": "string"}}, required=["a"]),
    )
    backend = RecordingBackend(schema)

    backend.render_schema()

    assert [(key, required) for key, _, required in backend.rendered] == [("a", True), ("b", False)]


@pytest.mark.parametrize("key", ["max_retry_count", "maxRetryCount"])
def test_render_schema__property_without_title__labels_with_title_cased_key(key: str) -> None:
    """Test that a property without a title is labelled with its key in title case."""
    backend = RecordingBackend(SettingsSchema.from_spec(object_spec({key: {"type": "integer"}})))

    backend.render_schema()

    assert backend.rendered == [(key, "Max Retry Count", False)]


def test_render_schema__no_properties__returns_empty_mapping_without_rendering() -> None:
    """Test that a schema without properties yields an empty mapping and renders nothing."""
    backend = RecordingBackend(SettingsSchema.from_spec({"type": "object", "$defs": {}}))

    assert backend.render_schema() == {}
    assert backend.rendered == []


def test_render_schema__additional_properties_entered__merges_them_at_top_level() -> None:
    """Test that additional-properties entries appear next to the declared properties in the output."""
    schema = SettingsSchema.from_spec(object_spec({"name": {"type": "string"}}, additionalProperties=True))
    backend = RecordingBackend(schema, values={"name": "app"}, additional_properties={"extra": 1})

    assert backend.render_schema() == {"name": "app", "extra": 1}


def test_render_schema__nested_additional_properties__flattens_them_into_the_nested_object() -> None:
    """Test that additional entries of a nested object appear directly inside that object."""
    schema = SettingsSchema.from_spec(
        object_spec({"nested": {"type": "object", "properties": {"x": {"type": "integer"}}}}),
    )
    backend = RecordingBackend(schema, values={"nested": {"x": 1, ADDITIONAL_PROPERTIES_KEY: {"k": 2}}})

    assert backend.render_schema() == {"nested": {"x": 1, "k": 2}}


def test_render_schema__object_property__returns_nested_mapping() -> None:
    """Test that a filled-in object property is returned as a mapping with its fields."""
    schema = SettingsSchema.from_spec(
        object_spec(
            {
                "db": {
                    "type": "object",
                    "properties": {"host": {"type": "string"}, "port": {"type": "integer"}},
                }
            }
        ),
    )
    backend = RecordingBackend(schema, values={"db": {"host": "localhost", "port": 5432}})

    output = backend.render_schema()

    assert output == {"db": {"host": "localhost", "port": 5432}}
