from abc import ABC, abstractmethod
from collections.abc import Callable, MutableMapping

from typing_extensions import Any, ParamSpec, TypeVar
from typing import Concatenate

from config_wizard.schema import SettingsSchema, ResolvedSettingsSchema, ResolvedSchema
from config_wizard.utils import to_title_case, unpack_additional_properties

P = ParamSpec("P")
T = TypeVar("T")
ADDITIONAL_PROPERTIES_KEY = "__additional_properties__"


class SettingsWizardBackend(ABC):
    """
    Abstract base class for settings wizard backends.

    Subclass this to implement a custom backend for interactive configuration wizards.
    The backend is responsible for rendering the schema, managing state, and handling user input.
    """

    schema: ResolvedSettingsSchema
    state: MutableMapping[str, Any]

    def __init__(self, schema: SettingsSchema):
        """
        Initialize the backend with a settings schema.

        Args:
            schema (SettingsSchema): The settings schema to use for the wizard.
        """
        self.schema = schema if isinstance(schema, ResolvedSettingsSchema) else schema.resolve_refs()
        self.state = self._init_state()

    @abstractmethod
    def _init_state(self) -> MutableMapping[str, Any]:
        """
        Create and return the initial state for the settings wizard.

        Returns:
            MutableMapping[str, Any]: The initial state mapping.

        """
        raise NotImplementedError("Subclasses must implement _init_state method.")

    @abstractmethod
    def _store_value(self, key: str, value: Any) -> None:
        """
        Store a value in the settings wizard state.

        Args:
            key (str): The key under which to store the value.
            value (Any): The value to store.

        """
        raise NotImplementedError("Subclasses must implement _store_value method.")

    @abstractmethod
    def _get_value(self, key: str) -> Any:
        """
        Retrieve a value from the settings wizard state.

        Args:
            key (str): The key of the value to retrieve.

        Returns:
            Any: The value associated with the key.

        """
        raise NotImplementedError("Subclasses must implement _get_value method.")

    @abstractmethod
    def _render_property(
        self,
        property_key: str,
        property_schema: ResolvedSchema,
        required: bool,
        is_item: bool,
    ) -> Any | None:
        """
        Render a property in the settings wizard UI.

        Args:
            property_key (str): The key of the property to render.
            property_schema (ResolvedSchema): The schema of the property to render.
            required (bool): Whether the property is required.
            is_item (bool): Whether the property is an item in a collection.

        Returns:
            Any | None: The rendered value of the property, or None if not applicable.

        """
        raise NotImplementedError("Subclasses must implement _render_property method.")

    @abstractmethod
    def _render_additional_properties(
        self,
        key: str,
        property_schema: ResolvedSchema,
        is_item: bool,
    ) -> dict[str, Any]:
        """
        Render additional properties in the settings wizard UI.

        Args:
            key (str): The key for the additional properties.
            property_schema (ResolvedSchema): The schema of the additional properties.
            is_item (bool): Whether the additional properties are items in a collection.

        Returns:
            dict[str, Any]: A dictionary of additional properties rendered in the UI.

        """
        raise NotImplementedError("Subclasses must implement _render_additional_properties method.")

    def render_schema(self) -> dict[str, Any]:
        """
        Render the settings wizard for the entire schema.

        Returns:
            dict[str, Any]: The user input data as a dictionary.
        """

        required = set(self.schema.required or [])

        # TODO: Support passing an instance of the schema to the backend to pre-populate the values in the wizard.

        # Render each property in the schema
        if not self.schema.properties:
            return {}

        prop: ResolvedSchema
        for prop_key, prop in self.schema.properties.items():
            if not prop.title:
                prop.title = to_title_case(prop_key)

            # TODO: Support passing a "container" in which the property is rendered.
            #  See `streamlit-pydantic` and how it handles optional properties
            value = self._render_property(
                property_key=prop_key,
                property_schema=prop,
                required=prop_key in required,
                is_item=False,
            )
            self._store_value(prop_key, value)

        if self.schema.additionalProperties:
            additional_properties = self._render_additional_properties(
                key=ADDITIONAL_PROPERTIES_KEY,
                property_schema=self.schema,
                is_item=False,
            )
            # Store additional properties in the state
            self._store_value(ADDITIONAL_PROPERTIES_KEY, additional_properties)

        # Unpack additional properties before returning
        return unpack_additional_properties(dict(self.state), ADDITIONAL_PROPERTIES_KEY)

    @abstractmethod
    def render_wizard(
        self,
        show_title: bool = True,
        submit_fn: Callable[Concatenate[dict[str, Any], P], T] = lambda x, *args, **kwargs: x,
        submit_text: str = "Submit",
        clear_on_submit: bool = True,
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> T | None:
        """
        Render the interactive settings wizard UI and handle submission.

        Args:
            show_title (bool): Whether to display the title of the wizard.
            submit_fn (Callable[Concatenate[dict[str, Any], P], T]):
                Function to call when the submit button is clicked.
                Should accept user input data as a dictionary and return a value of type T.
            submit_text (str): The text to display on the submit button.
            clear_on_submit (bool): Whether to clear the wizard state after submitting.
            *args: Additional positional arguments for the submit function.
            **kwargs: Additional keyword arguments for the submit function.

        Returns:
            T | None: The result of the submit function, or None if the wizard was cancelled or closed.

        """
        raise NotImplementedError("Subclasses must implement render_wizard method.")

    @abstractmethod
    def warning(self, *, title: str | None = None, message: str) -> None:
        """
        Display a warning message in the settings wizard UI.

        Args:
            title (str | None): The title of the warning (optional).
            message (str): The warning message to display.
        """
        raise NotImplementedError("Subclasses must implement warning method.")

    @abstractmethod
    def error(self, *, title: str | None = None, message: str) -> None:
        """
        Display an error message in the settings wizard UI.

        Args:
            title (str | None): The title of the error (optional).
            message (str): The error message to display.
        """
        raise NotImplementedError("Subclasses must implement error method.")
