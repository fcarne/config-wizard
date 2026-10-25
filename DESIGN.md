# `config-wizard`: Vision & Architecture

## 🎯 Overview

`config-wizard` is a framework-agnostic, interactive configuration generator that turns structured configuration schemas into user-friendly wizards.

Supports:

* ✅ JSON Schema / OpenAPI input
* ✅ Python class references (e.g., `myapp.settings:MySettings`)
* ✅ Output to YAML, JSON, or `.env`
* ✅ Multiple interactive backends: `Streamlit`, `Typer`, `Textual`

Built around a unified form model (based on Pydantic) to generate interactive forms from schemas.

---

## 🧠 Architecture

### Inputs

| FormatExampleDescription |                                          |                                        |
|--------------------------|------------------------------------------|----------------------------------------|
| JSON Schema              | `--schema config.schema.json`            | Raw JSON schema, OpenAPI format        |
| Class reference          | `--settings-path myapp.config:AppConfig` | Python import path to a Pydantic model |

### Core Flow

```
[Schema or Class]
     │
     ▼
[Parsed into Pydantic Model]
     │
     ▼
[Translated to FormSchema (list of FormFields)]
     │
     ▼
[Rendered by Backend UI (Streamlit, Typer, etc)]
     │
     ▼
[User Inputs → Pydantic Instance → Serialized Config File]
```

---

## 🔧 Project Structure

```
config_wizard/
├── __init__.py
├── cli.py                 # CLI entry point
├── loader.py              # Load class refs or JSON schemas
├── schema.py              # Converts to internal FormSchema
├── validator.py           # Builds & validates final config
├── exporter.py            # Outputs YAML, JSON, .env
├── backends/
│   ├── base.py            # Interface for all UIs
│   ├── streamlit/
│   │   ├── __init__.py
│   │   └── renderers.py
│   ├── typer/
│   └── textual/
└── types.py               # FormField, FormSchema, etc.

tests/
examples/
pyproject.toml
README.md
```

---

## 📦 Core Data Models

```
class FormField(BaseModel):
    name: str
    type: Literal["str", "int", "float", "bool", "enum", "model", "union"]
    required: bool
    default: Any = None
    enum_values: Optional[List[str]] = None
    children: Optional[List["FormField"]] = None
    description: Optional[str] = None
    constraints: dict = {}
    discriminator: Optional[str] = None
```

---

## 🖥️ Backend Interface

Each UI backend implements a standard interface:

```
class Backend(Protocol):
    def render(self, form_schema: List[FormField]) -> dict: ...
    def render_str(self, field: FormField): ...
    def render_enum(self, field: FormField): ...
    ...
```

Backends:

* `streamlit.render()`
* `typer.render()`
* `textual.render()`

Each backend can override rendering of types and group steps like a wizard.

---

## 🧪 Example Usage

### From Class Reference

```
config-wizard --settings-path myapp.settings:AppSettings --ui streamlit
```

### From JSON Schema

```
config-wizard --schema ./config.schema.json --ui typer
```

### Output

```
# config.yaml
host: 127.0.0.1
port: 8000
debug: false
```

---

## 🔮 Future Extensions

* ✅ Support for `dataclass`, `TypedDict`
* ✅ Support for discriminated unions
* ✅ Dynamic re-rendering (e.g., Streamlit) based on field values
* ✅ Validation preview before export
* ⏳ Support for saving/loading partial sessions
* ⏳ Plugin system for new backends or serializers

---

## 💡 Name Origin

> The name `config-wizard` was chosen for its clarity, memorability, and immediate association with interactive configuration tooling.

It reflects the goal: *take a schema or class → walk the user through an interactive wizard → produce a valid config file.*

---

## 🤝 Origin

This architecture and design was created in collaboration with ChatGPT in July 2025, inspired by Pydantic settings workflows, extensible backend UI design, and CLI-driven development patterns.
