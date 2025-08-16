import pytest
from openapi_pydantic import DataType, Schema, Discriminator

from config_wizard.mapper import InputType, property_to_input_type


@pytest.mark.parametrize(
    "input_type, expected_is_complex",
    [
        (InputType.EMAIL, False),
        (InputType.PASSWORD, False),
        (InputType.URI, False),
        (InputType.UUID, False),
        (InputType.IPV4, False),
        (InputType.IPV6, False),
        (InputType.TEXT, False),
        (InputType.FLOAT, False),
        (InputType.INTEGER, False),
        (InputType.BOOLEAN, False),
        (InputType.LIST, True),
        (InputType.SET, True),
        (InputType.TUPLE, True),
        (InputType.OBJECT, True),
        (InputType.DICT, True),
        (InputType.ANY, False),
        (InputType.NULL, False),
        (InputType.ENUM, False),
        (InputType.DISCRIMINATED_UNION, True),
        (InputType.UNION, True),
    ],
)
def test_input_type_is_complex(input_type: InputType, expected_is_complex: bool) -> None:
    """Test that the is_complex method returns the expected value for each InputType."""
    assert input_type.is_complex == expected_is_complex


@pytest.mark.parametrize(
    "json_schema, expected_input_type",
    [
        (Schema(type=DataType.STRING, format="email"), InputType.EMAIL),
        (Schema(type=DataType.STRING, format="password"), InputType.PASSWORD),
        (Schema(type=DataType.STRING, format="uri"), InputType.URI),
        (Schema(type=DataType.STRING, format="uuid"), InputType.UUID),
        (Schema(type=DataType.STRING, format="ipv4"), InputType.IPV4),
        (Schema(type=DataType.STRING, format="ipv6"), InputType.IPV6),
        (Schema(type=DataType.STRING), InputType.TEXT),
        (Schema(type=DataType.NUMBER), InputType.FLOAT),
        (Schema(type=DataType.INTEGER), InputType.INTEGER),
        (Schema(type=DataType.BOOLEAN), InputType.BOOLEAN),
        (
            Schema(type=DataType.ARRAY, items=Schema(type=DataType.STRING)),
            InputType.LIST,
        ),
        (
            Schema(
                type=DataType.ARRAY,
                items=Schema(type=DataType.STRING),
                uniqueItems=True,
            ),
            InputType.SET,
        ),
        (
            Schema(type=DataType.ARRAY, prefixItems=[Schema(type=DataType.STRING)]),
            InputType.TUPLE,
        ),
        (
            Schema(type=DataType.OBJECT, properties={"key": Schema(type=DataType.STRING)}),
            InputType.OBJECT,
        ),
        (
            Schema(type=DataType.OBJECT, additionalProperties=Schema(type=DataType.STRING)),
            InputType.DICT,
        ),
        (Schema(type=DataType.OBJECT), InputType.ANY),
        (Schema(type=DataType.NULL), InputType.NULL),
        (Schema(enum=["value1", "value2"]), InputType.ENUM),
        (
            Schema(
                type=DataType.STRING,
                discriminator=Discriminator(
                    propertyName="type",
                    mapping={"type1": "Type1Schema", "type2": "Type2Schema"},
                ),
                oneOf=[
                    Schema(type=DataType.OBJECT, title="Type1Schema"),
                    Schema(type=DataType.OBJECT, title="Type2Schema"),
                ],
            ),
            InputType.DISCRIMINATED_UNION,
        ),
        (
            Schema(
                anyOf=[
                    Schema(type=DataType.STRING),
                    Schema(type=DataType.INTEGER),
                ]
            ),
            InputType.UNION,
        ),
        (
            Schema(
                oneOf=[
                    Schema(type=DataType.STRING),
                    Schema(type=DataType.INTEGER),
                ]
            ),
            InputType.UNION,
        ),
        (Schema(type=DataType.NULL), InputType.NULL),
        (Schema(), InputType.ANY),
    ],
)
def test_property_to_input_type__json_schema__returns_correct_input_type(
    json_schema: Schema, expected_input_type: InputType
) -> None:
    """Test that property_to_input_type returns the expected InputType for various JSON schemas."""
    input_type = property_to_input_type(json_schema)

    assert input_type == expected_input_type
