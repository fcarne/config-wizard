from builtins import type as Type  # Developer notes: see https://github.com/python/mypy/issues/14205

from dataclasses import is_dataclass

from openapi_pydantic import DataType
from openapi_pydantic.v3.v3_1 import Schema
from pydantic import TypeAdapter, BaseModel, Field
from typing_extensions import Any
from typing import is_typeddict


class SettingsSchema(Schema):
    """
    Schema for the settings configuration.
    """

    _ref_map: dict[str, Any] | None = None

    @property
    def ref_map(self) -> dict[str, Any] | None:
        """
        Get the reference map for the schema.

        Returns:
            dict[str, Any] | None: The reference map if it exists, otherwise None.
        """
        return self._ref_map

    @ref_map.setter
    def ref_map(self, value: dict[str, Any] | None) -> None:
        """
        Set the reference map for the schema.

        Args:
            value (dict[str, Any] | None): The reference map to set.
        """
        if not isinstance(value, (dict, type(None))):
            raise TypeError("ref_map must be a dictionary or None.")
        self._ref_map = value

    @classmethod
    def from_spec(cls, spec: dict[str, Any]) -> "SettingsSchema":
        """
        Create an instance of SettingsSchema from a JSON Schema Definition or OpenAPI Specification.

        Args:
            spec (dict): The specification dictionary to convert.

        Returns:
            SettingsSchema: An instance of SettingsSchema.
        """
        settings_schema = cls.model_validate(spec)

        if "$defs" in spec:
            settings_schema._ref_map = spec["$defs"]

        return settings_schema

    @classmethod
    def from_schema(cls, schema: Type) -> "SettingsSchema":
        """
        Create an instance of SettingsSchema from a Pydantic model, TypedDict, or dataclass.

        Args:
            schema (SettingsSchemaInput): The schema to convert, which can be a Pydantic model, TypedDict, or dataclass.

        Returns:
            SettingsSchema: An instance of SettingsSchema.
        """

        if issubclass(schema, BaseModel):
            _json_schema = schema.model_json_schema()
        elif is_dataclass(schema) or is_typeddict(schema):
            type_adapter = TypeAdapter[Any](schema)
            _json_schema = type_adapter.json_schema()
        else:
            raise TypeError("The schema must be a Pydantic model, TypedDict, or dataclass.")

        settings_schema = cls.model_validate(_json_schema)
        settings_schema._ref_map = _json_schema.get("$defs", {})

        # TODO:
        #  Handle `Annotated` types for custom behavior, e.g., `Expander`
        #  see https://github.com/lukasmasuch/streamlit-pydantic/pull/64

        return settings_schema

    def resolve_refs(self, ref_map: dict[str, Any] | None = None) -> "ResolvedSettingsSchema":
        """
        Resolve references in the schema recursively.

        Args:
            ref_map (dict[str, Any] | None): A mapping of references to their definitions.
                If None, uses the already defined references in the schema.

        Returns:
            ResolvedSettingsSchema: A new instance of ResolvedSettingsSchema with resolved references.
        """
        if ref_map is None:
            ref_map = self._ref_map

        if ref_map is None:
            raise ValueError("No reference map provided for resolving references.")

        def _resolve(obj: Any) -> Any:
            if isinstance(obj, dict):
                if "$ref" in obj:
                    ref_key = obj["$ref"].split("/")[-1]
                    if ref_key in ref_map:
                        return _resolve(ref_map[ref_key])

                    raise KeyError(f"Reference '{ref_key}' not found in ref_map.")

                return {k: _resolve(v) for k, v in obj.items()}

            if isinstance(obj, list):
                return [_resolve(item) for item in obj]
            return obj

        resolved_schema = self.model_dump(by_alias=True, exclude_unset=True)

        try:
            resolved_schema = _resolve(resolved_schema)
            _schema = ResolvedSettingsSchema.model_validate(resolved_schema)
            return _schema
        except RecursionError as e:
            raise ValueError("Circular reference detected in schema resolution.") from e


class ResolvedSchema(Schema):
    """
    A subclass of SettingsSchema that indicates the schema has been resolved.
    """

    type: DataType = DataType.OBJECT  # Default type is OBJECT, so that it resolves to Any

    allOf: list["ResolvedSchema"] | None = None  # type: ignore[assignment]
    anyOf: list["ResolvedSchema"] | None = None  # type: ignore[assignment]
    oneOf: list["ResolvedSchema"] | None = None  # type: ignore[assignment]

    schema_not: "ResolvedSchema | None" = Field(default=None, alias="not")
    schema_if: "ResolvedSchema | None" = Field(default=None, alias="if")
    then: "ResolvedSchema | None" = None
    schema_else: "ResolvedSchema | None" = Field(default=None, alias="else")

    dependentSchemas: dict[str, "ResolvedSchema"] | None = None  # type: ignore[assignment]

    prefixItems: list["ResolvedSchema"] | None = None  # type: ignore[assignment]
    items: "ResolvedSchema | None" = None
    contains: "ResolvedSchema | None " = None

    properties: dict[str, "ResolvedSchema"] | None = None  # type: ignore[assignment]
    patternProperties: dict[str, "ResolvedSchema"] | None = None  # type: ignore[assignment]

    additionalProperties: "ResolvedSchema | bool | None" = None
    propertyNames: "ResolvedSchema | None" = None

    unevaluatedItems: "ResolvedSchema | None" = None
    unevaluatedProperties: "ResolvedSchema | None" = None

    contentSchema: "ResolvedSchema | None" = None


class ResolvedSettingsSchema(ResolvedSchema, SettingsSchema):
    """
    A schema that has been resolved, inheriting from both SettingsSchema and ResolvedSchema.
    This class is used to represent schemas with resolved references and additional properties.
    """
