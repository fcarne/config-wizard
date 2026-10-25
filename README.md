# config-wizard

**config-wizard** is a framework-agnostic, interactive configuration generator that transforms structured configuration schemas into user-friendly wizards.

[![Coverage](https://img.shields.io/badge/coverage-31%25-red)](#status)
[![PyPI Version](https://img.shields.io/pypi/v/config-wizard.svg)](https://pypi.org/project/config-wizard/)
[![Python Versions](https://img.shields.io/pypi/pyversions/config-wizard.svg)](https://pypi.org/project/config-wizard/)
[![License: MIT](https://img.shields.io/badge/License-MIT-lightgray.svg)](LICENSE)

## Status

Alpha. The schema core and the Streamlit backend are implemented. The command line, export to files and the other backends are planned, not available. The coverage figure covers the core only; the backends have no automated tests yet.

## Features

Implemented:

- Input from a Pydantic model, a dataclass, a TypedDict, or a JSON Schema / OpenAPI schema document
- `$ref` resolution, with clear errors for missing and circular references
- A single mapping from schema properties to input kinds shared by every backend
- A Streamlit backend covering text, numbers, booleans, enums, lists, sets, tuples, dictionaries, nested objects, unions and free-form JSON

Planned work is tracked in [`ROADMAP.md`](ROADMAP.md).

## Installation

From a clone of the repository, with the Streamlit extra:

```
poetry install --extras streamlit
```

## Example

Save this as `app.py` and run `poetry run streamlit run app.py`:

```python
import streamlit as st
from pydantic import BaseModel

from config_wizard.backends.streamlit import StreamlitSettingsWizard
from config_wizard.schema import SettingsSchema


class AppSettings(BaseModel):
    host: str = "127.0.0.1"
    port: int = 8000
    debug: bool = False


wizard = StreamlitSettingsWizard(SettingsSchema.from_schema(AppSettings))
settings = wizard.render_schema()

st.json(settings)
```

`render_schema()` draws the fields and returns the current values as a dictionary on every rerun.

## Project documents

- [`CONSTITUTION.md`](CONSTITUTION.md): principles, conventions and the glossary of terms used in the specs
- [`AGENTS.md`](AGENTS.md): layout, commands and workflow for contributors and coding agents
- [`ROADMAP.md`](ROADMAP.md): what is planned and in what order
- [`openspec/specs/`](openspec/specs/): the behavior the system guarantees

## License

MIT, see [`LICENSE`](LICENSE).
