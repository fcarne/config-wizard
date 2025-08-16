import pytest
from pydantic import BaseModel
from dataclasses import dataclass
from typing import TypedDict, Any


@pytest.fixture
def valid_openapi_spec() -> dict[str, Any]:
    """Fixture that provides a valid OpenAPI specification for testing."""
    return {
        "type": "object",
        "properties": {"name": {"type": "string"}, "age": {"type": "integer"}},
        "required": ["name", "age"],
    }


@pytest.fixture
def invalid_openapi_spec() -> dict[str, Any]:
    """Fixture that provides an invalid OpenAPI specification for testing."""
    return {"properties": {"name": {"type": "float"}, "age": {"type": "integer"}}}


@pytest.fixture
def user_model() -> type[BaseModel]:
    """Fixture that provides a Pydantic model for testing."""

    class UserModel(BaseModel):
        name: str
        age: int

    return UserModel


@pytest.fixture
def user_dataclass() -> type:
    """Fixture that provides a dataclass for testing."""

    @dataclass
    class UserData:
        name: str
        age: int

    return UserData


@pytest.fixture
def user_typeddict() -> type:
    """Fixture that provides a TypedDict for testing."""

    class UserDict(TypedDict):
        name: str
        age: int

    return UserDict


@pytest.fixture
def user_class() -> type:
    """Fixture that provides a class for testing."""

    class UserClass:
        name: str
        age: int

        def __init__(self, name: str, age: int):
            self.name = name
            self.age = age

    return UserClass
