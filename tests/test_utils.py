from collections.abc import Iterable

import pytest
from typing_extensions import Any

from config_wizard import utils
from openapi_pydantic import Schema


@pytest.mark.parametrize(
    "input_str,expected",
    [
        ("simple_test", "Simple Test"),
        ("camelCaseTest", "Camel Case Test"),
        ("already title", "Already Title"),
        ("with_multiple_words", "With Multiple Words"),
        ("Already Title Capitalized", "Already Title Capitalized"),
        ("     leadingAndTrailingSpaces     ", "Leading And Trailing Spaces"),
        ("with_numbers_123", "With Numbers 123"),
        ("with_special_chars_!@#", "With Special Chars !@#"),
        ("with___multiple___underscores", "With Multiple Underscores"),
        ("with-Mixed-Case", "With Mixed Case"),
        ("", ""),
    ],
)
def test_to_title_case(input_str: str, expected: str) -> None:
    """Test the to_title_case function."""
    assert utils.to_title_case(input_str) == expected


@pytest.mark.parametrize(
    "input_str,expected",
    [
        ("simpleTest", "simple-test"),
        ("camelCaseTest", "camel-case-test"),
        ("already-kebab", "already-kebab"),
        ("with_multiple_words", "with-multiple-words"),
        ("Already-Kebab-Cased", "already-kebab-cased"),
        ("     leadingAndTrailingSpaces     ", "leading-and-trailing-spaces"),
        ("with_numbers_123", "with-numbers-123"),
        ("with_special_chars_!@#", "with-special-chars-!@#"),
        ("with___multiple___underscores", "with-multiple-underscores"),
        ("with-Mixed-Case", "with-mixed-case"),
        ("", ""),
    ],
)
def test_to_kebab_case(input_str: str, expected: str) -> None:
    """Test the to_kebab_case function."""
    assert utils.to_kebab_case(input_str) == expected


@pytest.mark.parametrize(
    "value,schema_dict,expected",
    [
        (123, {"type": "integer"}, True),
        ("abc", {"type": "string"}, True),
        (123, {"type": "string"}, False),
        ({"a": 1}, {"type": "object", "properties": {"a": {"type": "integer"}}, "required": ["a"]}, True),
        ({"a": "wrong"}, {"type": "object", "properties": {"a": {"type": "integer"}}, "required": ["a"]}, False),
    ],
)
def test_is_assignable(value: Any, schema_dict: dict[str, Any], expected: bool) -> None:
    """Test the is_assignable function."""
    schema = Schema.model_validate(schema_dict)
    assert utils.is_assignable(value, schema) == expected


@pytest.mark.parametrize(
    "data,additional_key,expected",
    [
        (  # flat
            {"a": 1, "_add": {"b": 2}},
            "_add",
            {"a": 1, "b": 2},
        ),
        (  # nested
            {"a": {"_add": {"b": 2}}, "_add": {"c": 3}},
            "_add",
            {"a": {"b": 2}, "c": 3},
        ),
        (  # no additional
            {"a": 1},
            "_add",
            {"a": 1},
        ),
        (  # deeply nested
            {"a": {"b": {"_add": {"c": 3}}}, "_add": {"d": 4}},
            "_add",
            {"a": {"b": {"c": 3}}, "d": 4},
        ),
        (  # complex additional properties
            {"a": {"_add": {"b": 2, "c": {"d": 3}}}, "_add": {"e": 5}},
            "_add",
            {"a": {"b": 2, "c": {"d": 3}}, "e": 5},
        ),
        (  # additional key present but empty
            {"a": 1, "_add": {}},
            "_add",
            {"a": 1},
        ),
        (  # additional key not present
            {"a": 1, "b": 2},
            "_add",
            {"a": 1, "b": 2},
        ),
        (  # empty data
            {},
            "_add",
            {},
        ),
    ],
)
def test_unpack_additional_properties(data: dict[str, Any], additional_key: str, expected: dict[str, Any]) -> None:
    """Test the unpack_additional_properties function."""
    assert utils.unpack_additional_properties(data, additional_key) == expected


@pytest.mark.parametrize(
    "keys,expected",
    [
        ([], "new_item_0"),
        (["new_item_0"], "new_item_1"),
        (["new_item_0", "new_item_1", "new_item_2"], "new_item_3"),
        (["foo", "bar"], "new_item_0"),
        (["new_item_1", "new_item_3"], "new_item_4"),
        (["new_item_10", "new_item_2"], "new_item_11"),
    ],
)
def test_get_next_key(keys: Iterable[str], expected: str) -> None:
    assert utils.get_next_key(keys) == expected
