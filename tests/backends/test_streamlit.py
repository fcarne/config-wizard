import importlib.util
from collections.abc import Callable
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal

import pytest
from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from streamlit.testing.v1 import AppTest

PASSWORD_INPUT_TYPE = 1

pytestmark = pytest.mark.skipif(importlib.util.find_spec("streamlit") is None, reason="streamlit is not installed")


class VariantA(BaseModel):
    type: Literal["A"] = "A"
    name: str = ""


class VariantB(BaseModel):
    type: Literal["B"] = "B"
    age: int = 0


class DiscriminatedSettings(BaseModel):
    variant: VariantA | VariantB = Field(VariantB(age=7), discriminator="type")


def object_spec(properties: dict[str, Any], **extra: Any) -> dict[str, Any]:
    return {"type": "object", "$defs": {}, "properties": properties, **extra}


def two_wizards_app(spec) -> None:
    import streamlit as st

    from config_wizard.backends.streamlit import StreamlitSettingsWizard
    from config_wizard.schema import SettingsSchema

    st.session_state["results"] = {
        key: StreamlitSettingsWizard(SettingsSchema.from_spec(spec), key=key).render_schema() for key in ("a", "b")
    }


def test_init_state__two_wizards_with_different_keys__do_not_share_values(run_app: Callable[..., "AppTest"]) -> None:
    """Test that values entered in one wizard do not appear in another wizard on the same page."""
    app = run_app(two_wizards_app, object_spec({"name": {"type": "string", "default": "initial"}}))

    app.text_input[0].set_value("entered in a").run()

    assert app.session_state["results"] == {"a": {"name": "entered in a"}, "b": {"name": "initial"}}


def test_render_wizard__default_options__shows_title_description_and_save_button(
    run_wizard: Callable[..., "AppTest"],
) -> None:
    """Test that the default form shows the schema title as a subheader, the description and a Save button."""
    app = run_wizard(
        object_spec({"host": {"type": "string"}}, title="AppSettings", description="Main settings"),
        render="render_wizard",
    )

    assert [subheader.value for subheader in app.subheader] == ["AppSettings"]
    assert [markdown.value for markdown in app.markdown] == ["Main settings"]
    assert [button.label for button in app.button] == ["Save"]


def test_render_schema__field_changed__returns_updated_value_on_next_run(run_wizard: Callable[..., "AppTest"]) -> None:
    """Test that rendering without a form returns the current values on every rerun."""
    app = run_wizard(object_spec({"host": {"type": "string", "default": "localhost"}}))

    assert app.session_state["result"] == {"host": "localhost"}

    app.text_input[0].set_value("example.org").run()

    assert app.session_state["result"] == {"host": "example.org"}


def test_render_schema__titled_described_property__applies_common_presentation(
    run_wizard: Callable[..., "AppTest"],
) -> None:
    """Test that a field uses the title as label, the description as help, the default and the first example."""
    app = run_wizard(
        object_spec(
            {
                "host": {
                    "type": "string",
                    "title": "Host name",
                    "description": "Where to bind",
                    "default": "localhost",
                    "examples": ["example.org", "other.org"],
                }
            }
        )
    )

    field = app.text_input[0]
    assert (field.label, field.help, field.value, field.placeholder) == (
        "Host name",
        "Where to bind",
        "localhost",
        "example.org",
    )


def test_render_schema__read_only_property_with_default__renders_disabled_field_with_default(
    run_wizard: Callable[..., "AppTest"],
) -> None:
    """Test that a read-only string property with a default renders a disabled text field showing the default."""
    app = run_wizard(object_spec({"host": {"type": "string", "default": "localhost", "readOnly": True}}))

    assert [(field.label, field.value, field.disabled) for field in app.text_input] == [("Host", "localhost", True)]
    assert app.session_state["result"] == {"host": "localhost"}


def test_render_wizard__not_submitted__returns_nothing(run_wizard: Callable[..., "AppTest"]) -> None:
    """Test that the wizard returns nothing until the user submits."""
    app = run_wizard(object_spec({"host": {"type": "string"}}), render="render_wizard")

    assert app.session_state["result"] is None


def test_render_wizard__submitted_with_submit_function__returns_its_result(
    run_wizard: Callable[..., "AppTest"], tmp_path: Path
) -> None:
    """Test that submitting returns what the caller's submit function returns, here the path of a written file."""

    def write_file(data: dict[str, Any]) -> Path:
        path = tmp_path / "settings.txt"
        path.write_text(str(data))
        return path

    app = run_wizard(
        object_spec({"host": {"type": "string", "default": "localhost"}}),
        render="render_wizard",
        render_kwargs={"submit_fn": write_file},
    )

    app.button[0].click().run()

    assert app.session_state["result"] == tmp_path / "settings.txt"
    assert (tmp_path / "settings.txt").read_text() == "{'host': 'localhost'}"


def test_warning__title_and_message__shows_bold_title_then_message(run_wizard: Callable[..., "AppTest"]) -> None:
    """Test that a titled warning shows the title in bold followed by the message."""
    app = run_wizard(object_spec({}), render="warning", render_kwargs={"title": "Heads up", "message": "Port in use"})

    assert [warning.value for warning in app.warning] == ["**Heads up**:\nPort in use"]


def test_error__empty_message__shows_nothing(run_wizard: Callable[..., "AppTest"]) -> None:
    """Test that an error with an empty message displays nothing."""
    app = run_wizard(object_spec({}), render="error", render_kwargs={"title": "Failed", "message": ""})

    assert len(app.error) == 0


def test_render_schema__enum_with_several_options__shows_dropdown_with_default_selected(
    run_wizard: Callable[..., "AppTest"],
) -> None:
    """Test that an enum property renders a dropdown of its values with the default preselected."""
    app = run_wizard(
        object_spec({"mode": {"type": "string", "enum": ["option_a", "option_b", "option_c"], "default": "option_b"}})
    )

    assert [(box.options, box.value) for box in app.selectbox] == [(["option_a", "option_b", "option_c"], "option_b")]


def test_render_schema__enum_with_single_option__shows_no_widget_and_returns_the_value(
    run_wizard: Callable[..., "AppTest"],
) -> None:
    """Test that an enum allowing only one value renders nothing and returns that value."""
    app = run_wizard(object_spec({"only": {"type": "string", "enum": ["A"]}}))

    assert len(app.selectbox) == 0
    assert app.session_state["result"] == {"only": "A"}


def test_render_schema__boolean_property__shows_toggle_in_default_position(
    run_wizard: Callable[..., "AppTest"],
) -> None:
    """Test that a boolean property with default false renders a toggle in the off position."""
    app = run_wizard(object_spec({"flag": {"type": "boolean", "default": False}}))

    assert [(toggle.label, toggle.value) for toggle in app.toggle] == [("Flag", False)]


def test_render_schema__bounded_integer__shows_slider_with_bounds_and_step(
    run_wizard: Callable[..., "AppTest"],
) -> None:
    """Test that an integer with both bounds renders a slider from the minimum to the maximum with step 1."""
    app = run_wizard(object_spec({"n": {"type": "integer", "minimum": 1, "maximum": 10}}))

    assert [(slider.min, slider.max, slider.step) for slider in app.slider] == [(1, 10, 1)]


def test_render_schema__integer_with_exclusive_minimum__shows_number_field_starting_one_step_above(
    run_wizard: Callable[..., "AppTest"],
) -> None:
    """Test that an exclusive minimum of 0 on an integer renders a number field with minimum 1."""
    app = run_wizard(object_spec({"m": {"type": "integer", "exclusiveMinimum": 0}}))

    assert [field.min for field in app.number_input] == [1]
    assert len(app.slider) == 0


def test_render_schema__password_format__shows_masked_text_field(run_wizard: Callable[..., "AppTest"]) -> None:
    """Test that a string with the password format renders a masked text field."""
    app = run_wizard(object_spec({"secret": {"type": "string", "format": "password"}}))

    assert [field.proto.type for field in app.text_input] == [PASSWORD_INPUT_TYPE]


def test_render_schema__invalid_email__shows_error_and_returns_entered_value(
    run_wizard: Callable[..., "AppTest"],
) -> None:
    """Test that a value that is not an email address is flagged beside the field and still returned."""
    app = run_wizard(object_spec({"mail": {"type": "string", "format": "email"}}))

    app.text_input[0].set_value("not-an-email").run()

    assert [error.value for error in app.error] == ["Please enter a valid email address."]
    assert app.session_state["result"] == {"mail": "not-an-email"}


def test_render_schema__value_not_matching_pattern__shows_error_naming_the_pattern(
    run_wizard: Callable[..., "AppTest"],
) -> None:
    """Test that a value that does not match the property's pattern is flagged with the expected pattern."""
    app = run_wizard(object_spec({"slug": {"type": "string", "pattern": "^[a-z]+$"}}))

    app.text_input[0].set_value("ABC").run()

    assert [error.value for error in app.error] == ["Invalid format, expected format: ^[a-z]+$"]


def add_item_button(app: "AppTest") -> Any:
    return next(button for button in app.button if button.label == "Add Item")


def test_render_schema__add_item_on_list_with_one_row__shows_second_empty_row(
    run_wizard: Callable[..., "AppTest"],
) -> None:
    """Test that pressing Add Item on a list with one row shows a second, empty row."""
    app = run_wizard(object_spec({"xs": {"type": "array", "items": {"type": "string"}, "minItems": 1}}))

    assert [field.value for field in app.text_input] == [None]

    add_item_button(app).click().run()

    assert [field.value for field in app.text_input] == [None, None]


def test_render_schema__tuple_with_prefix_items__renders_row_widgets_by_position_and_returns_tuple(
    run_wizard: Callable[..., "AppTest"],
) -> None:
    """Test that tuple items are rendered by position, a number field then a text field, and a tuple is returned."""
    app = run_wizard(
        object_spec(
            {
                "pair": {
                    "type": "array",
                    "prefixItems": [{"type": "integer"}, {"type": "string"}],
                    "minItems": 2,
                    "maxItems": 2,
                }
            }
        )
    )

    app.number_input[0].set_value(3)
    app.text_input[0].set_value("x").run()

    assert (len(app.number_input), len(app.text_input)) == (1, 1)
    assert app.session_state["result"] == {"pair": (3, "x")}


def test_render_schema__list_at_max_items__disables_add_item(run_wizard: Callable[..., "AppTest"]) -> None:
    """Test that Add Item is disabled once a list holds the maximum number of items."""
    app = run_wizard(object_spec({"xs": {"type": "array", "items": {"type": "string"}, "minItems": 2, "maxItems": 2}}))

    assert add_item_button(app).disabled


def test_render_schema__set_with_duplicate_entries__shows_error_and_returns_deduplicated_set(
    run_wizard: Callable[..., "AppTest"],
) -> None:
    """Test that entering the same value twice in a set shows a duplicate-items error and returns the set once."""
    app = run_wizard(object_spec({"s": {"type": "array", "uniqueItems": True, "items": {"type": "integer"}}}))

    add_item_button(app).click().run()
    app.number_input[0].set_value(1).run()
    add_item_button(app).click().run()
    app.number_input[1].set_value(1).run()

    assert [error.value for error in app.error] == [
        "Duplicate items found in the set. Please ensure all items are unique."
    ]
    assert app.session_state["result"] == {"s": {1}}


def test_render_schema__add_item_on_dict__adds_row_with_next_free_key(run_wizard: Callable[..., "AppTest"]) -> None:
    """Test that Add Item on a dict with keys new_item_0 and new_item_1 adds a row keyed new_item_2."""
    app = run_wizard(
        object_spec(
            {
                "d": {
                    "type": "object",
                    "additionalProperties": {"type": "integer"},
                    "default": {"new_item_0": 1, "new_item_1": 2},
                }
            }
        )
    )

    add_item_button(app).click().run()

    assert [field.value for field in app.text_input] == ["new_item_0", "new_item_1", "new_item_2"]


def test_render_schema__dict_with_default__shows_rows_with_default_entries(
    run_wizard: Callable[..., "AppTest"],
) -> None:
    """Test that a dict of integers with a default shows one prefilled row per entry and returns the default."""
    app = run_wizard(
        object_spec(
            {
                "d": {
                    "type": "object",
                    "additionalProperties": {"type": "integer"},
                    "default": {"a": 1, "b": 2},
                }
            }
        )
    )

    assert [field.value for field in app.text_input] == ["a", "b"]
    assert [field.value for field in app.number_input] == [1, 2]
    assert app.session_state["result"] == {"d": {"a": 1, "b": 2}}


def test_render_schema__nested_object__shows_titled_group_with_its_fields_in_order(
    run_wizard: Callable[..., "AppTest"],
) -> None:
    """Test that an object property renders a heading followed by its fields in declaration order."""
    app = run_wizard(
        object_spec({"db": {"type": "object", "properties": {"host": {"type": "string"}, "port": {"type": "integer"}}}})
    )

    elements = app.main.children.values()
    assert [
        (element.type, getattr(element, "label", None) or getattr(element, "value", None)) for element in elements
    ] == [
        ("subheader", "Db"),
        ("text_input", "Host"),
        ("number_input", "Port"),
    ]


def test_render_schema__optional_integer__offers_integer_and_null_alternatives(
    run_wizard: Callable[..., "AppTest"],
) -> None:
    """Test that a property that is an integer or null renders a selector offering both alternatives."""
    app = run_wizard(object_spec({"o": {"anyOf": [{"type": "integer"}, {"type": "null"}]}}))

    assert [box.options for box in app.selectbox] == [["integer", "null"]]


def test_render_schema__null_alternative_selected__shows_no_input_and_returns_null(
    run_wizard: Callable[..., "AppTest"],
) -> None:
    """Test that selecting the null alternative of an optional property hides the input and returns null."""
    app = run_wizard(object_spec({"o": {"anyOf": [{"type": "integer"}, {"type": "null"}]}}))

    app.selectbox[0].set_value("null").run()

    assert len(app.number_input) == 0
    assert app.session_state["result"] == {"o": None}


def test_render_schema__free_form_property_with_valid_json__returns_parsed_value(
    run_wizard: Callable[..., "AppTest"],
) -> None:
    """Test that JSON entered in a free-form field is parsed and returned as a mapping."""
    app = run_wizard(object_spec({"j": {}}))

    app.text_area[0].set_value('{"a": 1}').run()

    assert app.session_state["result"] == {"j": {"a": 1}}


def test_render_schema__free_form_property_with_invalid_json__shows_error_and_returns_raw_text(
    run_wizard: Callable[..., "AppTest"],
) -> None:
    """Test that invalid JSON in a free-form field is flagged and the raw text is returned."""
    app = run_wizard(object_spec({"j": {}}))

    app.text_area[0].set_value("{a: 1}").run()

    assert [error.value for error in app.error] == ["Invalid JSON format. Please enter a valid JSON object."]
    assert app.session_state["result"] == {"j": "{a: 1}"}


def test_render_schema__discriminated_union_with_default__preselects_matching_alternative(
    run_wizard: Callable[..., "AppTest"],
) -> None:
    """Test that the alternative whose discriminator matches the default is preselected and shows that value."""
    app = run_wizard(DiscriminatedSettings)

    assert [box.index for box in app.selectbox] == [1]
    assert [(field.label, field.value) for field in app.text_input] == [("Type", "B")]
