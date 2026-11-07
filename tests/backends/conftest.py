from collections.abc import Callable
from typing import TYPE_CHECKING, Any

import pytest

if TYPE_CHECKING:
    from streamlit.testing.v1 import AppTest


def _wizard_app(source, render, wizard_kwargs, render_kwargs) -> None:
    import streamlit as st

    from config_wizard.backends.streamlit import StreamlitSettingsWizard
    from config_wizard.schema import SettingsSchema

    schema = SettingsSchema.from_spec(source) if isinstance(source, dict) else SettingsSchema.from_schema(source)
    wizard = StreamlitSettingsWizard(schema, **wizard_kwargs)
    st.session_state["result"] = getattr(wizard, render)(**render_kwargs)


@pytest.fixture
def run_app() -> Callable[..., "AppTest"]:
    """Fixture that runs a self-contained script function in a simulated Streamlit app and returns the app."""

    def run(script: Callable[..., None], *args: Any) -> "AppTest":
        from streamlit.testing.v1 import AppTest

        app = AppTest.from_function(script, default_timeout=10, args=args).run()
        assert not app.exception
        return app

    return run


@pytest.fixture
def run_wizard(run_app: Callable[..., "AppTest"]) -> Callable[..., "AppTest"]:
    """Fixture that runs the Streamlit wizard for a schema source in a simulated app and returns the app."""

    def run(
        source: Any,
        render: str = "render_schema",
        wizard_kwargs: dict[str, Any] | None = None,
        render_kwargs: dict[str, Any] | None = None,
    ) -> "AppTest":
        return run_app(_wizard_app, source, render, wizard_kwargs or {}, render_kwargs or {})

    return run
