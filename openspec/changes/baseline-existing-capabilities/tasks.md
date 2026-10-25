# Tasks

## 1. Constitution

- [ ] 1.1 Write `CONSTITUTION.md` with: purpose (schema to interactive wizard to config file), architectural principles (JSON-Schema-native `ResolvedSchema`, `InputType` as the single dispatch vocabulary, backends implement `SettingsWizardBackend`, core stays UI-free with UI toolkits as optional extras), conventions (Google-style docstrings on public and private functions and classes, full type hints checked by mypy with the pydantic plugin, Ruff at 120 columns, pyupgrade `--py310-plus`, one test per spec scenario), non-goals, and the rule that behavior changes go through an OpenSpec change. Verify every principle matches `design.md` Decisions and no section restates the specs.
- [ ] 1.3 Add a glossary section to `CONSTITUTION.md` mapping input kind, settings schema, resolved schema, reference map, backend and wizard to their code names (`InputType`, `SettingsSchema`, `ResolvedSettingsSchema`, `ref_map`, `SettingsWizardBackend`, `StreamlitSettingsWizard`). Verify each code name resolves with `grep -rn` in `config_wizard/`.
- [ ] 1.2 Add a "Planned" section to `CONSTITUTION.md` listing the roadmap carried over from `DESIGN.md` (CLI, YAML/JSON/.env exporter, validation before export, Typer and Textual backends, partial session save/load, backend and serializer plugins), marked as not implemented. Verify each item is absent from `config_wizard/`.

## 2. Agent guidance

- [ ] 2.1 Write `AGENTS.md` covering: project summary in two sentences, link to `CONSTITUTION.md`, repository layout as it exists (`config_wizard/schema.py`, `mapper.py`, `utils.py`, `backends/base.py`, `backends/streamlit.py`, empty `typer.py` and `textual.py`, `tests/`, `openspec/`), commands (`make install`, `make format`, `make lint`, `make test`, `poetry run streamlit run test_wizard.py` for the manual harness), the OpenSpec workflow (`/opsx:explore`, `/opsx:propose`, `/opsx:apply`, `/opsx:archive`; specs in `openspec/specs/`), and the definition of done (lint and tests pass, spec scenarios covered by tests). Verify each listed command runs successfully or, for the Streamlit harness, starts without import errors.
- [ ] 2.2 Write `CLAUDE.md` containing only the line `@AGENTS.md`. Verify the file has exactly that one line.
- [ ] 2.3 Add `.claude/settings.json` allowing `make` targets, `openspec *`, `poetry run pytest*`, `poetry run ruff*`, `poetry run mypy*`, and read-only git (`git status`, `git diff`, `git log`), with no blanket `poetry run *`. Add `.claude/settings.local.json` to `.gitignore`. Verify the JSON parses and `git check-ignore .claude/settings.local.json` succeeds.

## 3. README

- [ ] 3.1 Rewrite `README.md`: keep the one-line description and badges, list implemented features (Pydantic/dataclass/TypedDict and JSON Schema/OpenAPI input, `$ref` resolution, Streamlit backend) separately from planned ones, replace the `FormField` backend interface with a minimal working Python example using `SettingsSchema.from_schema` and `StreamlitSettingsWizard(...).render_schema()`, and link to `CONSTITUTION.md`, `AGENTS.md` and `openspec/specs/`. Verify the example runs with `poetry run streamlit run` on a scratch copy and that the README no longer mentions `FormField` or claims a working CLI.
- [ ] 3.2 Replace the hardcoded 100% coverage badge in `README.md` with a static badge showing the measured total from `make test`. Verify the badge value equals the `TOTAL` line of the coverage report.

## 4. OpenSpec configuration

- [ ] 4.1 Add a `context:` entry to `openspec/config.yaml` stating that `CONSTITUTION.md` holds project principles and conventions, that the codebase targets Python 3.10+, and that baseline known issues are listed in the archived `baseline-existing-capabilities` design. Keep the existing commented examples. Verify with `openspec list --json` that the root still resolves and the YAML parses.
- [ ] 4.2 Add `rules:` to `openspec/config.yaml`: proposal (state what is out of scope; link follow-ups instead of bundling them), specs (describe verified behavior only; use behavior vocabulary from the glossary, not code names; every scenario is test-ready; known defects go to design, not requirements), design (record evidence for each known issue), tasks (each task names its verification; tests and docs land in the group that needs them). Verify `openspec validate baseline-existing-capabilities --strict` still passes and `openspec instructions specs --change baseline-existing-capabilities --json` shows the rules.

## 5. Retire DESIGN.md

- [ ] 5.1 Make sure `DESIGN.md` is restorable: if `git log --oneline -- DESIGN.md` is empty, copy it to the session scratchpad and report the absolute path to the user before continuing. Verify the copy is byte-identical with `cmp`.
- [ ] 5.2 Delete `DESIGN.md` and remove any references to it. Verify `grep -rn "DESIGN.md" --exclude-dir=openspec --exclude-dir=.git .` returns nothing.

## 6. Integration checks

- [ ] 6.1 Run `openspec validate baseline-existing-capabilities --strict` and verify it reports the change as valid.
- [ ] 6.2 Run `make test` and verify the suite still passes with the same 98 tests, confirming no code was touched.
- [ ] 6.3 Run `git status` and verify the only changes are `AGENTS.md`, `CLAUDE.md`, `CONSTITUTION.md`, `README.md`, `.gitignore`, `.claude/settings.json`, `openspec/config.yaml`, the change directory, and the removal of `DESIGN.md`.

## Workflow follow-up

- Archive the change with `/opsx:archive` to create `openspec/specs/` for the five capabilities, then confirm with `openspec list --specs`.
- Open `add-ci-pipeline` (skip_specs) for a GitHub Actions workflow running lint, mypy, tests and `openspec validate --all --strict`, plus a pull request template linking the OpenSpec change.
- Open follow-up changes for the remaining Known Issues in `design.md`; a natural first one is a Streamlit `AppTest` suite plus fixes for issues 3 to 7.
