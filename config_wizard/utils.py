import re
from collections.abc import Iterable
from typing_extensions import Any

import jsonschema
from openapi_pydantic import Schema


def to_title_case(s: str) -> str:
    """
    Convert a string to title case, replacing underscores with spaces.

    Args:
        s (str): The string to convert.

    Returns:
        str: The converted string in title case.
    """

    # Convert to snake_case from camelCase, PascalCase, kebab-case, etc.
    s = re.sub(r"(?<!^)(?=[A-Z])", "_", s).lower()
    s = s.replace(" ", "_")  # Remove all spaces
    s = re.sub(r"[-_]+", "_", s)  # Replace multiple underscores or hyphens with a single underscore

    # Replace underscores with spaces and capitalize each word
    return s.replace("_", " ").strip().title()


def to_kebab_case(s: str) -> str:
    """
    Convert a string to kebab case, replacing spaces with hyphens.

    Args:
        s (str): The string to convert.

    Returns:
        str: The converted string in kebab case.
    """

    # Convert to snake_case from camelCase, PascalCase, kebab-case, etc.
    s = re.sub(r"(?<!^)(?=[A-Z])", "_", s).lower()
    s = s.replace(" ", "_")  # Remove all spaces
    s = re.sub(r"[-_]+", "_", s)  # Replace multiple underscores or hyphens with a single underscore

    # Replace underscores with hyphens and return
    return s.replace("_", "-").strip("-").lower()


def is_assignable(value: Any, schema: Schema) -> bool:
    """
    Check if a value is assignable to a schema.

    Args:
        value (Any): The value to check.
        schema (Schema): The schema to check against.

    Returns:
        bool: True if the value is assignable to the schema, False otherwise.
    """
    try:
        jsonschema.validate(instance=value, schema=schema.model_dump(exclude_unset=True))
        return True
    except jsonschema.ValidationError:
        return False


def unpack_additional_properties(data: dict, additional_properties_key: str) -> dict:
    """
    Recursively merge additional properties (under a reserved key) into the parent dictionary.

    Args:
        data (dict): The dictionary to unpack.
        additional_properties_key (str): The reserved key for additional properties.

    Returns:
        dict: The dictionary with additional properties merged in.
    """
    result = {}
    for k, v in data.items():
        if k == additional_properties_key and isinstance(v, dict):
            for add_k, add_v in v.items():
                if isinstance(add_v, dict):
                    result[add_k] = unpack_additional_properties(add_v, additional_properties_key)
                else:
                    result[add_k] = add_v
        elif isinstance(v, dict):
            result[k] = unpack_additional_properties(v, additional_properties_key)
        else:
            result[k] = v
    return result


def get_next_key(keys: Iterable[str]) -> str:
    """
    Given a collection of keys, return the next available 'new_item_{n}' key.
    """
    max_idx = max(
        (int(m.group(1)) for k in keys if (m := re.match(r"new_item_(\d+)", str(k)))),
        default=-1,
    )
    return f"new_item_{max_idx + 1}"
