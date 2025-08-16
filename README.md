# config-wizard

**config-wizard** is a framework-agnostic, interactive configuration generator that transforms structured configuration schemas into user-friendly wizards.

[![Coverage Status](https://img.shields.io/badge/coverage-100%25-brightgreen)](htmlcov/index.html)
[![PyPI Version](https://img.shields.io/pypi/v/config-wizard.svg)](https://pypi.org/project/config-wizard/)
[![Python Versions](https://img.shields.io/pypi/pyversions/config-wizard.svg)](https://pypi.org/project/config-wizard/)
[![License: MIT](https://img.shields.io/badge/License-MIT-lightgray.svg)](LICENSE)
## Features
- Supports JSON Schema / OpenAPI input
- Supports Python class references (e.g., `myapp.settings:MySettings`)
- Output to YAML, JSON, or `.env`
- Multiple interactive backends: Streamlit, Typer, Textual
- Unified form model (based on Pydantic) for generating interactive forms from schemas

## Architecture

### Inputs
- **JSON Schema:** `--schema config.schema.json` (Raw JSON schema, OpenAPI format)
- **Class reference:** `--settings-path myapp.config:AppConfig` (Python import path to a Pydantic model)

## Backend Interface

Each UI backend implements a standard interface:

```
class Backend(Protocol):
    def render(self, form_schema: List[FormField]) -> dict: ...
    def render_str(self, field: FormField): ...
    def render_enum(self, field: FormField): ...
    ...
```

Backends:
- `streamlit.render()`
- `typer.render()`
- `textual.render()`

Each backend can override rendering of types and group steps like a wizard.

## Example Usage

- From Class Reference:
  ```
  config-wizard --settings-path myapp.settings:AppSettings --ui streamlit
  ```
- From JSON Schema:
  ```
  config-wizard --schema ./config.schema.json --ui typer
  ```
- Output:
  ```
  # config.yaml
  host: 127.0.0.1
  port: 8000
  debug: false
  ```
