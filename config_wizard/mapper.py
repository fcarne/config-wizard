from enum import Enum

from openapi_pydantic import Schema


class InputType(str, Enum):
    """Enum for input types."""

    # Text input types
    TEXT = "text"
    EMAIL = "email"
    PASSWORD = "password"
    URI = "uri"
    UUID = "uuid"
    FILE_PATH = "file_path"
    DIRECTORY_PATH = "directory_path"
    IPV4 = "ipv4"
    IPV6 = "ipv6"

    # Number input types
    INTEGER = "integer"
    FLOAT = "float"

    # Date and time input types
    DATE = "date"
    TIME = "time"
    DATETIME = "datetime"
    DURATION = "duration"

    # Boolean input type
    BOOLEAN = "boolean"

    # Select input types
    ENUM = "enum"

    # Complex input types
    LIST = "list"
    TUPLE = "tuple"
    SET = "set"
    DICT = "dict"
    OBJECT = "object"
    UNION = "union"
    DISCRIMINATED_UNION = "discriminated_union"

    # Any input types
    ANY = "any"
    NULL = "null"

    @property
    def is_complex(self) -> bool:
        """
        Check if the input type is complex (not a simple text or number).

        Returns:
            bool: True if the input type is complex, False otherwise.
        """
        return self in {
            InputType.LIST,
            InputType.TUPLE,
            InputType.SET,
            InputType.DICT,
            InputType.OBJECT,
            InputType.UNION,
            InputType.DISCRIMINATED_UNION,
        }


def property_to_input_type(prop: Schema) -> InputType:
    """
    Convert a Schema property to an InputType.

    Args:
        prop (Schema): The Schema property to convert.

    Returns:
        InputType: The corresponding InputType.
    """
    if prop.enum:
        return InputType.ENUM

    if prop.discriminator:
        return InputType.DISCRIMINATED_UNION

    if prop.anyOf or prop.oneOf:
        return InputType.UNION

    # TODO: We are not handling `allOf` here, which might be needed in the future.

    match prop.type:
        case "string":
            match prop.schema_format:
                case "email":
                    return InputType.EMAIL
                case "password":
                    return InputType.PASSWORD
                case "uri":
                    return InputType.URI
                case "uuid":
                    return InputType.UUID
                case "ipv4":
                    return InputType.IPV4
                case "ipv6":
                    return InputType.IPV6
                case _:
                    return InputType.TEXT
        case "number":
            return InputType.FLOAT
        case "integer":
            return InputType.INTEGER
        case "boolean":
            return InputType.BOOLEAN
        case "array":
            if prop.prefixItems:
                return InputType.TUPLE

            if prop.uniqueItems:
                return InputType.SET

            return InputType.LIST
        case "object":
            if prop.properties:
                return InputType.OBJECT
            if prop.additionalProperties:
                return InputType.DICT

            return InputType.ANY
        case "null":
            return InputType.NULL
        case _:
            return InputType.ANY
