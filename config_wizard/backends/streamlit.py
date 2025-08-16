import json
import re
from copy import deepcopy
from datetime import datetime, date, time
from collections.abc import MutableMapping, Callable, Iterable

import streamlit as st

from openapi_pydantic.v3.v3_0 import DataType
from streamlit.delta_generator import DeltaGenerator
from typing_extensions import Any, TypedDict
from typing import Concatenate, Literal

from config_wizard.backends.base import SettingsWizardBackend, P, T
from config_wizard.mapper import property_to_input_type, InputType
from config_wizard.schema import SettingsSchema, ResolvedSchema
from config_wizard.utils import to_kebab_case, to_title_case, get_next_key, is_assignable

KEY_SEPARATOR = "."


class _DefaultStreamlitInputKwargs(TypedDict, total=False):
    """
    Default arguments for Streamlit input widgets.

    Used to standardize widget parameters for consistent rendering and state management.
    """

    key: str
    disabled: bool
    label: str
    label_visibility: Literal["visible", "hidden", "collapsed"]
    help: str | None
    placeholder: str | None

    value: Any | None


class _NumberInputKwargs(TypedDict, total=False):
    """Arguments for Streamlit number input widgets."""

    step: float | int
    min_value: float | int
    max_value: float | int
    format: str


class _StringInputKwargs(TypedDict, total=False):
    """Arguments for Streamlit string input widgets."""

    max_chars: int
    type: Literal["default", "password"]  # Streamlit supports 'default' and 'password' types


class _SelectboxKwargs(TypedDict, total=False):
    """Arguments for Streamlit selectbox widgets."""

    options: Iterable
    index: int
    format_func: Callable[[str], str] | None


def _is_add_button_disabled(property_schema: ResolvedSchema, current_length: int) -> bool:
    """Determine if the add button should be displayed based on the schema and current length."""
    if property_schema.readOnly:
        return True

    if property_schema.maxItems is not None and current_length >= property_schema.maxItems:
        return True

    return False


def _is_clear_button_disabled(property_schema: ResolvedSchema) -> bool:
    """Determine if the clear button should be displayed based on the schema."""
    if property_schema.readOnly:
        return False

    return True


def _is_remove_button_disabled(property_schema: ResolvedSchema, current_length: int) -> bool:
    """Determine if the remove button should be displayed based on the schema and current length."""
    if property_schema.readOnly:
        return True

    if property_schema.minItems is not None and current_length <= property_schema.minItems:
        return True

    return False


class StreamlitSettingsWizard(SettingsWizardBackend):
    """
    Streamlit backend for the config-wizard interactive settings wizard.

    Implements the abstract backend interface using Streamlit widgets.
    Supports rendering all OpenAPI-compatible input types, managing state, and handling user interactions for
    configuration schemas.

    Example usage:
        wizard = StreamlitSettingsWizard(schema)
        result = wizard.render_wizard()
    """

    key: str
    container: DeltaGenerator

    _state_key: str
    _run_id: int

    def __init__(
        self,
        schema: SettingsSchema,
        key: str | None = None,
        container: DeltaGenerator = st,
    ):
        """
        Initialize the Streamlit settings wizard backend.

        Args:
            schema (SettingsSchema): The settings schema to use for the wizard.
            key (str | None): Optional key for widget state isolation.
            container (DeltaGenerator): Streamlit container to render widgets in.
        """
        self.container = container
        self.key = key or schema.title or to_kebab_case(schema.__class__.__name__)

        super().__init__(schema)

    def _init_state(self) -> MutableMapping[str, Any]:
        self._run_id = st.session_state.setdefault("run_id", 0)
        self._state_key = f"{self.key}-data"

        return st.session_state.setdefault(self._state_key, {})

    def _store_value(self, key: str, value: Any) -> None:
        state = self.state

        key_parts = key.split(KEY_SEPARATOR)
        for i, part in enumerate(key_parts):
            if i == len(key_parts) - 1:
                state[part] = value
                return

            if part not in state:
                state[part] = {}
            state = state[part]

    def _get_value(self, key: str) -> Any:
        state = self.state

        key_parts = key.split(KEY_SEPARATOR)
        for i, part in enumerate(key_parts):
            if i == len(key_parts) - 1:
                if part not in state:
                    return None
                return state[part]

            if part not in state:
                state[part] = {}
            state = state[part]

        return None

    def _get_default_streamlit_input_kwargs(
        self, property_key: str, property_schema: ResolvedSchema, is_item: bool
    ) -> _DefaultStreamlitInputKwargs:
        """
        Get the default arguments for Streamlit input widgets.

        Args:
            property_key (str): The key of the property.
            property_schema (ResolvedSchema): The schema of the property.
            is_item (bool): Whether the property is an item in a collection.
        Returns:
            _DefaultStreamlitInputKwargs: The default arguments for the input widget.
        """
        return _DefaultStreamlitInputKwargs(
            key=f"{self._run_id}-{self.key}-{property_key}",
            label=property_schema.title or property_key,
            label_visibility="collapsed" if is_item else "visible",
            disabled=property_schema.readOnly or False,
            help=property_schema.description if not is_item else None,
            value=property_schema.default,
            placeholder=(property_schema.examples[0] if property_schema.examples else property_schema.example),
        )

    def _render_enum_input(
        self,
        property_key: str,
        property_schema: ResolvedSchema,
        container: DeltaGenerator,
        is_item: bool,
    ) -> str | int | float | bool | None:
        """
        Render an enum input widget in Streamlit.
        Returns the selected value from the enum options, or None.
        """
        input_kwargs = self._get_default_streamlit_input_kwargs(property_key, property_schema, is_item)
        kwargs: _SelectboxKwargs = {}

        options = property_schema.enum or []

        default_value = input_kwargs.pop("value", None)
        if default_value is not None:
            kwargs["index"] = options.index(default_value)

        # If there is only one option then there is no choice for the user to be made,
        # so simply return the value (This is relevant for discriminator properties)
        if len(options) == 1:
            return options[0]

        kwargs["options"] = options
        return container.selectbox(**(input_kwargs | kwargs))

    def _render_datetime_input(
        self,
        property_key: str,
        property_schema: ResolvedSchema,
        input_type: Literal[InputType.DATE, InputType.DATETIME, InputType.TIME],
        container: DeltaGenerator,
        is_item: bool,
    ) -> datetime | date | time | None:
        """
        Render a datetime input widget in Streamlit.
        Returns a datetime, date, or time object, or None.
        """
        input_kwargs = self._get_default_streamlit_input_kwargs(property_key, property_schema, is_item)

        if input_type == InputType.DATE:
            return container.date_input(**input_kwargs)
        if input_type == InputType.TIME:
            return container.time_input(**input_kwargs)

        # Streamlit does not have a dedicated datetime input,
        # see: https://github.com/streamlit/streamlit/issues/6089

        with container.container():
            if not is_item:
                container.subheader(input_kwargs.pop("label"))
            if input_kwargs["help"]:
                container.text(input_kwargs.pop("help", None))

            date_col, time_col = container.columns(2)
            with date_col:
                selected_date = date_col.date_input(
                    **(input_kwargs | {"label": "Date", "key": f"{input_kwargs['key']}-date-input"})
                )
            with time_col:
                selected_time = time_col.time_input(
                    **(input_kwargs | {"label": "Time", "key": f"{input_kwargs['key']}-time-input"})
                )

            return datetime.combine(selected_date, selected_time)

    def _render_boolean_input(
        self,
        property_key: str,
        property_schema: ResolvedSchema,
        container: DeltaGenerator,
        is_item: bool,
    ) -> bool | None:
        """
        Render a boolean input widget in Streamlit.
        Returns the selected boolean value, or None.
        """
        input_kwargs = self._get_default_streamlit_input_kwargs(property_key, property_schema, is_item)
        del input_kwargs["placeholder"]  # Streamlit toggle does not support placeholder

        if is_item:
            container.markdown("##")

        return container.toggle(
            **input_kwargs,
        )

    def _render_number_input(
        self,
        property_key: str,
        property_schema: ResolvedSchema,
        input_type: Literal[InputType.INTEGER, InputType.FLOAT],
        container: DeltaGenerator,
        is_item: bool,
    ) -> int | float | None:
        """
        Render a number input widget in Streamlit.
        Returns the entered number value (int or float), or None.
        """
        input_kwargs = self._get_default_streamlit_input_kwargs(property_key, property_schema, is_item)

        kwargs: _NumberInputKwargs = {}

        number = float if input_type == InputType.FLOAT else int
        if input_type == InputType.FLOAT:
            kwargs["format"] = "%f"

        if property_schema.multipleOf is not None:
            kwargs["step"] = number(property_schema.multipleOf)
        elif number is int:
            kwargs["step"] = 1
        else:
            kwargs["step"] = 0.01

        if property_schema.minimum is not None:
            kwargs["min_value"] = number(property_schema.minimum)
        if property_schema.exclusiveMinimum is not None:
            kwargs["min_value"] = number(property_schema.exclusiveMinimum) + kwargs["step"]

        if property_schema.maximum is not None:
            kwargs["max_value"] = number(property_schema.maximum)
        if property_schema.exclusiveMaximum is not None:
            kwargs["max_value"] = number(property_schema.exclusiveMaximum) - kwargs["step"]

        if "min_value" in kwargs and "max_value" in kwargs:
            del input_kwargs["placeholder"]  # Streamlit slider does not support placeholder
            return container.slider(**(input_kwargs | kwargs))

        return container.number_input(**(input_kwargs | kwargs))

    def _render_text_input(
        self,
        property_key: str,
        property_schema: ResolvedSchema,
        input_type: Literal[
            InputType.TEXT,
            InputType.PASSWORD,
            InputType.EMAIL,
            InputType.UUID,
            InputType.URI,
            InputType.IPV4,
            InputType.IPV6,
            InputType.FILE_PATH,
            InputType.DIRECTORY_PATH,
        ],
        container: DeltaGenerator,
        is_item: bool,
    ) -> str | None:
        """
        Render a text input widget in Streamlit.
        Returns the entered text value, or None.
        """
        input_kwargs = self._get_default_streamlit_input_kwargs(property_key, property_schema, is_item)

        kwargs: _StringInputKwargs = {}
        # TODO: Handle minLength for text inputs
        if property_schema.maxLength is not None:
            kwargs["max_chars"] = property_schema.maxLength

        if input_type == InputType.PASSWORD:
            kwargs["type"] = "password"

        error_message = None

        if not property_schema.pattern:
            match input_type:
                case InputType.EMAIL:
                    property_schema.pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
                    error_message = "Please enter a valid email address."
                case InputType.UUID:
                    property_schema.pattern = r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
                    error_message = "Please enter a valid UUID."
                case InputType.URI:
                    property_schema.pattern = r"^(.+://)?[^\s/$.?#].[^\s]*$"
                    error_message = "Please enter a valid URI."
                case InputType.IPV4:
                    property_schema.pattern = (
                        r"^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)"
                        r"\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"
                    )
                    error_message = "Please enter a valid IPv4 address."
                case InputType.IPV6:
                    property_schema.pattern = r"^([0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$"
                    error_message = "Please enter a valid IPv6 address."
                case InputType.FILE_PATH:
                    property_schema.pattern = r"^([a-zA-Z]:)?(\\[a-zA-Z0-9_.-]+)+\\?$"
                    error_message = "Please enter a valid file path."
                case InputType.DIRECTORY_PATH:
                    property_schema.pattern = r"^([a-zA-Z]:)?(\\[a-zA-Z0-9_.-]+)+\\?$"
                    error_message = "Please enter a valid directory path."

        if property_schema.pattern:
            # Streamlit does not support regex validation directly,
            # so we will use the pattern to validate the input after submission.
            text_col, validation_col = container.columns(2, vertical_alignment="bottom")
            with text_col:
                input_value = text_col.text_input(
                    **(input_kwargs | kwargs),
                )
            with validation_col:
                if input_value and not re.match(property_schema.pattern, input_value):
                    validation_col.error(error_message or f"Invalid format, expected format: {property_schema.pattern}")

            return input_value

        return container.text_input(**(input_kwargs | kwargs))

    def _render_list_item_input(
        self,
        index: int,
        current_length: int,
        value: Any,
        property_key: str,
        property_schema: ResolvedSchema,
        container: DeltaGenerator,
    ) -> tuple[Any | None, bool]:
        """
        Render an input widget for an item in a list.
        Returns a tuple of (value, False) or (None, True) if the item was removed.
        """

        item_property_schema = deepcopy(property_schema)
        item_property_schema.title = f"Item #{index + 1}"
        if value is not None:
            item_property_schema.default = value

        item_placeholder = container.empty()

        with item_placeholder.container():
            input_item_col, remove_item_col = container.columns([4, 1])

            with remove_item_col:
                if remove_item_col.button(
                    "Remove",
                    key=f"{property_key}-remove",
                    disabled=_is_remove_button_disabled(property_schema, current_length),
                ):
                    # Remove the item from the list
                    item_placeholder.empty()
                    return None, True

            with input_item_col:
                return (
                    self._render_property(
                        property_key=property_key,
                        property_schema=property_schema,
                        required=False,  # Items in a list are not required by default
                        is_item=True,
                        container=input_item_col,
                    ),
                    False,
                )

    def _render_list_input(
        self,
        property_key: str,
        property_schema: ResolvedSchema,
        input_type: Literal[InputType.LIST, InputType.TUPLE, InputType.SET],
        container: DeltaGenerator,
        is_item: bool,
    ) -> list[Any] | tuple[Any, ...] | set[Any]:
        """
        Render a list/tuple/set input widget in Streamlit.
        Returns the entered list, tuple, or set value.
        """
        input_kwargs = self._get_default_streamlit_input_kwargs(property_key, property_schema, is_item)

        container.subheader(input_kwargs.pop("label"))
        if input_kwargs["help"]:
            container.markdown(input_kwargs.pop("help", None))

        # Default value handling
        if (stored_value := self._get_value(property_key)) is not None:
            data_list = list(stored_value)
        elif input_kwargs["value"] is not None:
            data_list = list(input_kwargs["value"])
        else:
            # Default to a list with as many items as the minimum items specified in the schema
            data_list = [None] * (property_schema.minItems if property_schema.minItems is not None else 0)

        output_list = []

        add_item_col, clear_item_col, _ = container.columns(3)
        with add_item_col:
            if add_item_col.button(
                "Add Item",
                key=f"{input_kwargs['key']}-add-item",
                disabled=_is_add_button_disabled(property_schema, len(data_list)),
            ):
                data_list.append(None)

        with clear_item_col:
            if clear_item_col.button(
                "Clear Items",
                key=f"{input_kwargs['key']}-clear-items",
                disabled=_is_clear_button_disabled(property_schema),
            ):
                data_list = [None] * (property_schema.minItems if property_schema.minItems is not None else 0)

        # Developer notes:
        #  For tuples, `prefixItems` must be defined, while for other collections, `items` is used.
        #  Moreover, `i` will always be less than or equal to the length of `prefixItems` for tuples.

        for i, item in enumerate(data_list):
            item_schema: ResolvedSchema = (
                property_schema.prefixItems[i]  # type: ignore[index, assignment]
                if input_type == InputType.TUPLE
                else property_schema.items
            )
            item_input_type = property_to_input_type(item_schema)

            output_item, is_removed = self._render_list_item_input(
                index=i,
                current_length=len(data_list),
                value=item,
                property_key=f"{property_key}{KEY_SEPARATOR}{i}",
                property_schema=item_schema,
                container=container,
            )
            if not is_removed:
                output_list.append(output_item)

            if item_input_type.is_complex and i != len(data_list) - 1:
                container.markdown("---")

        if input_type == InputType.SET:
            if len(output_list) != len(set(output_list)):
                st.error("Duplicate items found in the set. Please ensure all items are unique.")

        container.markdown("---")

        match input_type:
            case InputType.LIST:
                return output_list
            case InputType.TUPLE:
                return tuple(output_list)
            case InputType.SET:
                return set(output_list)

    def _render_dict_item_input(
        self,
        current_length: int,
        key: str,
        value: Any | None,
        property_key: str,
        property_schema: ResolvedSchema,
        container: DeltaGenerator,
    ) -> tuple[str, Any | None, bool]:
        """
        Render an input widget for an item in a dictionary.
        Returns a tuple of (key, value, False) or (None, None, True) if the item was removed.
        """
        value_schema = deepcopy(property_schema)
        if value is not None:
            value_schema.default = value

        item_placeholder = container.empty()

        with item_placeholder.container():
            item_key_col, item_value_col, remove_item_col = container.columns([2, 3, 1], vertical_alignment="bottom")

            with remove_item_col:
                if remove_item_col.button(
                    "Remove",
                    key=f"{property_key}-remove",
                    disabled=_is_remove_button_disabled(property_schema, current_length),
                ):
                    # Remove the item from the dictionary
                    item_placeholder.empty()
                    return "", None, True

            with item_key_col:
                item_key = item_key_col.text_input(
                    label="Key",
                    key=f"{property_key}-key",
                    value=key,
                    disabled=property_schema.readOnly or False,
                )

            with item_value_col:
                item_value = self._render_property(
                    property_key=f"{property_key}-value",
                    property_schema=value_schema,
                    required=False,  # Items in a dict are not required by default
                    is_item=False,
                    container=item_value_col,
                )
            return item_key, item_value, False

    def _render_dict_items(
        self,
        container: DeltaGenerator,
        data_dict: dict[str, Any],
        input_kwargs: _DefaultStreamlitInputKwargs,
        property_key: str,
        property_schema: ResolvedSchema,
    ) -> dict[str, Any]:
        """
        Render the items of a dictionary input widget in Streamlit.
        Returns the entered dictionary value.
        """
        output_dict: dict[str, Any] = {}

        add_item_col, clear_item_col, _ = container.columns(3)
        with add_item_col:
            if add_item_col.button(
                "Add Item",
                key=f"{input_kwargs['key']}-add-item",
                disabled=_is_add_button_disabled(property_schema, len(data_dict)),
            ):
                # Add a new item with a unique key to the dictionary
                data_dict[get_next_key(data_dict.keys())] = None

        with clear_item_col:
            if clear_item_col.button(
                "Clear Items",
                key=f"{input_kwargs['key']}-clear-items",
                disabled=_is_clear_button_disabled(property_schema),
            ):
                data_dict = {}

        # Developer notes:
        #  For dicts, `additionalProperties` must be defined, and it can be a schema or a boolean.
        item_schema: ResolvedSchema = (
            property_schema.additionalProperties  # type: ignore[assignment]
            if not isinstance(property_schema.additionalProperties, bool)
            else ResolvedSchema(  # `additionalProperties: true` case, fallback to ANY
                type=DataType.OBJECT, title="Value"
            )
        )
        item_input_type = property_to_input_type(item_schema)

        for index, (key, value) in enumerate(data_dict.items()):
            item_property_key = f"{property_key}{KEY_SEPARATOR}{key}"
            output_item_key, output_item_value, is_removed = self._render_dict_item_input(
                current_length=len(data_dict),
                key=key,
                value=value,
                property_key=item_property_key,
                property_schema=item_schema,
                container=container,
            )

            # TODO:
            #  Should we store a dict like {"key": output_item_key, "value": output_item_value} instead?
            #  This would help us avoid overwriting keys in the output_dict and more easily deal with duplicate keys.

            if not is_removed:
                # Check if the new key is not overwriting another existing key
                if len(set(output_dict.keys())) != len(set(output_dict.keys()).union({output_item_key})):
                    output_dict[key] = output_item_value
                else:
                    output_dict[output_item_key] = output_item_value

            if item_input_type.is_complex and index != len(data_dict) - 1:
                container.markdown("---")

        container.markdown("---")

        return output_dict

    def _render_dict_input(
        self,
        property_key: str,
        property_schema: ResolvedSchema,
        container: DeltaGenerator,
        is_item: bool,
    ) -> dict[str, Any]:
        """
        Render a dictionary input widget in Streamlit.
        Returns the entered dictionary value.
        """
        input_kwargs = self._get_default_streamlit_input_kwargs(property_key, property_schema, is_item)

        container.subheader(input_kwargs.pop("label"))
        if input_kwargs["help"]:
            container.markdown(input_kwargs.pop("help", None))

        # Default value handling
        if (stored_value := self._get_value(property_key)) is not None:
            data_dict = stored_value
        elif input_kwargs["value"] is not None:
            data_dict = input_kwargs["value"]
        else:
            # Default to an empty dictionary if no default value is provided
            data_dict = {}

        return self._render_dict_items(container, data_dict, input_kwargs, property_key, property_schema)

    def _render_object_properties(
        self,
        parent_property_key: str,
        parent_property_schema: ResolvedSchema,
        container: DeltaGenerator,
        is_item: bool,
    ) -> dict[str, Any]:
        """
        Render the properties of an object in Streamlit.
        Returns the entered object value as a dictionary.
        """
        output_object: dict[str, Any] = {}

        # Developer notes:
        #  Schemas mapped to objects must have `properties` defined.
        property_schema: ResolvedSchema
        for property_key, property_schema in parent_property_schema.properties.items():  # type: ignore[union-attr]
            if not property_schema.title:
                property_schema.title = to_title_case(property_key)
            full_property_key = f"{parent_property_key}{KEY_SEPARATOR}{property_key}"

            value = self._render_property(
                property_key=full_property_key,
                property_schema=property_schema,
                required=property_key in (parent_property_schema.required or set()),
                is_item=is_item,
                container=container,
            )

            output_object[property_key] = value

        # Handle additional properties if defined
        if parent_property_schema.additionalProperties:
            output_object.update(
                self._render_additional_properties(
                    key=f"{parent_property_key}{KEY_SEPARATOR}additionalProperties",
                    property_schema=parent_property_schema,
                    is_item=is_item,
                    container=container,
                )
            )

        return output_object

    def _render_object_input(
        self,
        property_key: str,
        property_schema: ResolvedSchema,
        container: DeltaGenerator,
        is_item: bool,
    ) -> dict[str, Any]:
        """
        Render an object input widget in Streamlit.
        Returns the entered object value as a dictionary.
        """
        input_kwargs = self._get_default_streamlit_input_kwargs(property_key, property_schema, is_item)

        if is_item:
            container.caption(input_kwargs.pop("label"))
        else:
            container.subheader(input_kwargs.pop("label"))

        if input_kwargs["help"]:
            container.markdown(input_kwargs.pop("help", None))

        return self._render_object_properties(
            parent_property_key=property_key,
            parent_property_schema=property_schema,
            container=container,
            is_item=is_item,
        )

    def _render_union_input(
        self,
        property_key: str,
        property_schema: ResolvedSchema,
        input_type: Literal[InputType.UNION, InputType.DISCRIMINATED_UNION],
        container: DeltaGenerator,
        is_item: bool,
    ) -> Any | None:
        """
        Render a union input widget in Streamlit.
        Returns the entered value from the selected union option, or None.
        """
        input_kwargs = self._get_default_streamlit_input_kwargs(property_key, property_schema, is_item)
        kwargs: _SelectboxKwargs = {}

        # Handle default value for union types and select the correct schema and input type
        union_schemas: list[ResolvedSchema] = deepcopy(property_schema.anyOf or property_schema.oneOf or [])

        if (value := input_kwargs.pop("value")) is not None:
            if input_type == InputType.DISCRIMINATED_UNION:
                # For discriminated unions, we need to select the correct schema based on the discriminator

                # Developer notes:
                #  Discriminated unions must have a `discriminator` property that must be in the `properties`.
                discriminator = property_schema.discriminator.propertyName  # type: ignore[union-attr]
                selected_index = next(
                    i
                    for i, schema in enumerate(union_schemas)
                    if schema.properties[discriminator].const == value[discriminator]  # type: ignore[index]
                )

            else:
                # For regular unions, we select the first schema that is assignable to the value.
                selected_index = next(i for i, schema in enumerate(union_schemas) if is_assignable(value, schema))

            union_schemas[selected_index].default = value
            kwargs["index"] = selected_index

        schemas_mapping = {
            (
                to_kebab_case(schema.title)
                if schema.title
                else (f"{schema.type.value} {'(' + schema.schema_format + ')' if schema.schema_format else ''}".strip())
            ): schema
            for schema in union_schemas
        }

        container.subheader(input_kwargs.pop("label"))
        if input_kwargs["help"]:
            container.markdown(input_kwargs.pop("help"))

        kwargs["options"] = schemas_mapping.keys()
        kwargs["format_func"] = lambda x: schemas_mapping[x].title or x

        # Render a selectbox to choose the union type
        selected_schema = container.selectbox(
            **(
                input_kwargs
                | kwargs
                | {
                    "key": f"{input_kwargs['key']}-select-union",
                    "label": "Union options",
                }
            )
        )

        output_data = self._render_property(
            property_key=property_key,
            property_schema=schemas_mapping[selected_schema],
            required=True,  # TODO: Handle required properties in unions
            is_item=is_item,
            container=container,
        )

        container.markdown("---")
        return output_data

    def _render_any_input(
        self,
        property_key: str,
        property_schema: ResolvedSchema,
        container: DeltaGenerator,
        is_item: bool,
    ) -> Any | None:
        """
        Render an input widget for any type in Streamlit.
        Returns the entered value, which can be of any type, or None.
        """
        input_kwargs = self._get_default_streamlit_input_kwargs(property_key, property_schema, is_item)
        # Streamlit does not have a dedicated input for 'any' type, a JSON input would be ideal,
        # but we can use a text area for the user to input any value.
        with container.container():
            input_value = container.text_area(**input_kwargs)

            if input_value:
                try:
                    return json.loads(input_value)
                except json.JSONDecodeError:
                    container.error("Invalid JSON format. Please enter a valid JSON object.")

            return input_value

    def _render_property(
        self,
        property_key: str,
        property_schema: ResolvedSchema,
        required: bool,
        is_item: bool,
        container: DeltaGenerator | None = None,
    ) -> Any | None:
        input_type = property_to_input_type(property_schema)

        container = container or self.container

        match input_type:
            case InputType.ENUM:
                return self._render_enum_input(property_key, property_schema, container, is_item)
            case InputType.DATE | InputType.DATETIME | InputType.TIME:  # TODO: Support DURATION type
                return self._render_datetime_input(
                    property_key,
                    property_schema,
                    input_type,
                    container,
                    is_item,
                )
            case InputType.BOOLEAN:
                return self._render_boolean_input(property_key, property_schema, container, is_item)
            case InputType.INTEGER | InputType.FLOAT:
                return self._render_number_input(property_key, property_schema, input_type, container, is_item)
            case (
                InputType.TEXT
                | InputType.PASSWORD
                | InputType.EMAIL
                | InputType.UUID
                | InputType.URI
                | InputType.IPV4
                | InputType.IPV6
                | InputType.FILE_PATH
                | InputType.DIRECTORY_PATH
            ):
                return self._render_text_input(property_key, property_schema, input_type, container, is_item)
            case InputType.LIST | InputType.TUPLE | InputType.SET:
                return self._render_list_input(property_key, property_schema, input_type, container, is_item)
            case InputType.DICT:
                return self._render_dict_input(property_key, property_schema, container, is_item)
            case InputType.OBJECT:
                return self._render_object_input(property_key, property_schema, container, is_item)
            case InputType.UNION | InputType.DISCRIMINATED_UNION:
                return self._render_union_input(property_key, property_schema, input_type, container, is_item)
            case InputType.NULL:
                return None
            case InputType.ANY:
                return self._render_any_input(property_key, property_schema, container, is_item)

        self.warning(
            message=(
                f"The type of the following property is currently not supported: "
                f"{property_schema.title or property_key}"
            ),
            container=container,
        )
        raise NotImplementedError(f"Input type '{input_type}' is not implemented for Streamlit backend.")

    def _render_additional_properties(
        self,
        key: str,
        property_schema: ResolvedSchema,
        is_item: bool,
        container: DeltaGenerator | None = None,
    ) -> dict[str, Any]:
        """
        Render additional properties in the settings wizard UI.

        Args:
            key (str): The key for the additional properties.
            property_schema (ResolvedSchema): The schema of the additional properties.
            is_item (bool): Whether the additional properties are items in a collection.
            container (DeltaGenerator | None): Optional Streamlit container.

        Returns:
            dict[str, Any]: A dictionary of additional properties rendered in the UI.
        """
        container = container or self.container

        input_kwargs = self._get_default_streamlit_input_kwargs(key, property_schema, is_item)

        container.subheader("Additional Properties")

        # Default value handling
        if (stored_value := self._get_value(key)) is not None:
            data_dict = stored_value
        else:
            # Default to an empty dictionary if no default value is provided
            data_dict = {}

        return self._render_dict_items(
            container=container,
            data_dict=data_dict,
            input_kwargs=input_kwargs,
            property_key=key,
            property_schema=property_schema,
        )

    def render_wizard(
        self,
        show_title: bool = True,
        submit_fn: Callable[Concatenate[dict[str, Any], P], T] = lambda x, *args, **kwargs: x,
        submit_text: str = "Save",
        clear_on_submit: bool = True,
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> T | None:
        """
        Render the interactive settings wizard UI in Streamlit and handle submission.

        Args:
            show_title (bool): Whether to display the title of the wizard.
            submit_fn (Callable[Concatenate[dict[str, Any], P], T]):
                Function to call when the submit/save button is clicked.
                Should accept user input data as a dictionary and return a value of type T.
            submit_text (str): The text to display on the submit/save button.
            clear_on_submit (bool): Whether to clear the wizard state after submitting.
            *args: Additional positional arguments for the submit function.
            **kwargs: Additional keyword arguments for the submit function.

        Returns:
            T: The result of the submit function, if provided. Otherwise, returns the user input data as a dictionary.

        """

        with self.container.form(key=self.key, clear_on_submit=clear_on_submit):
            if show_title:
                st.subheader(self.schema.title)
            if self.schema.description:
                st.markdown(self.schema.description)

            output_data = self.render_schema()

            if st.form_submit_button(label=submit_text):
                return submit_fn(output_data, *args, **kwargs)

        return None

    def warning(
        self,
        *,
        title: str | None = None,
        message: str,
        container: DeltaGenerator | None = None,
    ) -> None:
        """
        Display a warning message in the Streamlit app.

        Args:
            title (str | None): Optional title for the warning.
            message (str): Warning message to display.
            container (DeltaGenerator | None): Optional Streamlit container.
        """

        if not message:
            return

        warning = f"**{title}**:\n{message}" if title else message
        (container or self.container).warning(warning)

    def error(
        self,
        *,
        title: str | None = None,
        message: str,
        container: DeltaGenerator | None = None,
    ) -> None:
        """
        Display an error message in the Streamlit app.

        Args:
            title (str | None): Optional title for the error.
            message (str): Error message to display.
            container (DeltaGenerator | None): Optional Streamlit container.
        """

        if not message:
            return

        error = f"**{title}**:\n{message}" if title else message
        (container or self.container).error(error)
