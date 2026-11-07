import datetime
import decimal
import enum
import typing
import uuid
from typing import Annotated

import pydantic.networks
import pydantic_extra_types.color
import pydantic_extra_types.payment
import streamlit as st
from pydantic import ConfigDict

from config_wizard.backends.streamlit import StreamlitSettingsWizard
from config_wizard.schema import SettingsSchema


class TestEnum(enum.StrEnum):
    OPTION_A = "option_a"
    OPTION_B = "option_b"
    OPTION_C = "option_c"


class NestedSchema(pydantic.BaseModel):
    nested_string: str
    nested_integer: int


class DiscriminatedUnionSchemaA(pydantic.BaseModel):
    type: typing.Literal["A"] = "A"
    name: str


class DiscriminatedUnionSchemaB(pydantic.BaseModel):
    type: typing.Literal["B"] = "B"
    age: int


class SchemaTest(pydantic.BaseModel):
    """A schema for testing various Pydantic field types and features."""

    model_config = ConfigDict(
        extra="allow",
    )

    string_field: str
    email_field: pydantic.EmailStr
    password_field: pydantic.SecretStr
    url_field: pydantic.HttpUrl
    uuid_field: uuid.UUID
    file_path_field: pydantic.FilePath
    directory_path_field: pydantic.DirectoryPath
    color_field: pydantic_extra_types.color.Color

    const_string_field: typing.Literal["constant_value"]
    const_integer_field: typing.Literal[42]
    const_float_field: Annotated[float, pydantic.Field(json_schema_extra={"const": 3.14})]
    const_boolean_field: typing.Literal[True]

    integer_field: int
    float_field: float

    date_field: datetime.date
    time_field: datetime.time
    datetime_field: datetime.datetime
    timedelta_field: datetime.timedelta

    boolean_field: bool

    enum_field: TestEnum
    multi_enum_field: set[TestEnum]

    list_field: list[str]
    tuple_field: tuple[int, int]
    set_field: set[int]
    dict_field: dict[str, int]
    nested_field: NestedSchema

    union_field: int | str
    discriminated_union_field: DiscriminatedUnionSchemaA | DiscriminatedUnionSchemaB = pydantic.Field(
        discriminator="type"
    )

    optional_field: str | None = None
    default_field: str = "default_value"

    bytes_field: bytes
    decimal_field: decimal.Decimal

    constrained_int_field: Annotated[int, pydantic.Field(gt=0, lt=100)]
    constrained_str_field: Annotated[str, pydantic.Field(min_length=3, max_length=10)]

    any_field: typing.Any

    dict_int_key_field: dict[int, str]
    list_uuid_field: list[uuid.UUID]

    ipv4_field: pydantic.networks.IPv4Address
    ipv6_field: pydantic.networks.IPv6Address
    ipvany_field: pydantic.networks.IPvAnyAddress

    payment_card_field: pydantic_extra_types.payment.PaymentCardNumber

    secret_bytes_field: pydantic.SecretBytes
    json_field: pydantic.JsonValue

    postgres_dns_field: pydantic.PostgresDsn

    dict_str_any_field: dict[bool, typing.Any]


schema = SettingsSchema.from_schema(SchemaTest)
wizard = StreamlitSettingsWizard(schema)

st.title("Settings Wizard")
st.write("Please fill out the following settings:")
settings = wizard.render_schema()

st.json(settings)
st.json(wizard.state)
