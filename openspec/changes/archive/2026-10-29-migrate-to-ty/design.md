# Design

## Context

See `proposal.md` for motivation. Evidence from a scratch clone of `origin/main` (commit `ad34aa6`) with the uv environment and all extras; nothing in the repository was touched:

| # | Finding | Evidence |
|---|---------|----------|
| 1 | ty gives stable results here | 36 diagnostics with ty 0.0.91 and with 0.0.95, the same files and the same rule counts, although 0.0.93, 0.0.94 and 0.0.95 were all released within two days |
| 2 | ty understands Pydantic natively | On a probe model, mypy with the Pydantic plugin reported 3 problems, ty 5 (including the wrong-type argument `Model(name=1)` and a warning that an extra argument is discarded), and pyrefly's default preset 4 |
| 3 | mypy checks Streamlit weakly today | The isolated hook passes with `--ignore-missing-imports`; the project environment's mypy 2.4.0 reports 11 errors, 7 of them `call-overload`, and `jsonschema` has no stubs there |
| 4 | The 36 come from three places | `schema.py` 19 (12 `invalid-mutable-override`, 7 `invalid-attribute-override`); `streamlit.py` 16 (7 `no-matching-overload`, 2 `invalid-assignment`, 2 `not-subscriptable`, 2 `unresolved-attribute`, 1 each of `invalid-parameter-default`, `invalid-argument-type` and `unknown-argument`); `tests/test_schema.py` 1 (`invalid-assignment`, a deliberate wrong-type assignment) |
| 5 | The existing ignores are dead under ty | A blanket `# type: ignore` suppresses, but `# type: ignore[assignment]` does not, so all 13 mypy-coded comments (7 in `schema.py`, 5 in `streamlit.py`, 1 in a test) suppress nothing, and `unused-ignore-comment` does not flag them |
| 6 | The official hook is environment-dependent | `ty-pre-commit` runs `uv check` at a pinned revision, leaves the environment alone, and reports 28 diagnostics after a default `uv sync` (including 2 `unresolved-import` for Streamlit) against 36 with all extras |
| 7 | A local run is deterministic | `uv run --all-extras ty check` reports 36 in about 0.6 s, detects the project environment by itself, and installs the extras as a side effect |
| 8 | Per-file overrides work | A `[[tool.ty.overrides]]` entry scoped to `config_wizard/schema.py` removed its 19 diagnostics, leaving 17 |
| 9 | The editor is covered | `astral-sh.ty` is Astral's official VS Code extension; its documentation says it turns off the Python extension's own language server automatically, and offers `ty.disableLanguageServices` to keep another server |
| 10 | Pyrefly is a viable fallback | pyrefly 1.4.0 is marked Production/Stable; its default preset reports 25 errors (12 `schema.py`, 13 `streamlit.py`), its official hook in an isolated environment reports 24 `missing-import` errors, and its extension is `meta.pyrefly` |

Constraints that shape the approach:
- ty is Beta and pre-1.0, so releases can change diagnostics.
- The `streamlit.py` typing smells are real, but the backend has no tests, so reshaping its calls to satisfy a checker is a separate, riskier change.
- The project rule is that lint and type findings are fixed or narrowly suppressed with the rule named, never silenced wholesale.

## Goals / Non-Goals

**Goals:**
- ty is the only type checker, run locally, in the editor and from pre-commit, against the lock-pinned environment.
- Zero diagnostics, with every suppression named and traceable to a cause.
- No runtime behavior change.

**Non-Goals:**
- Fixing the Streamlit typing smells or redesigning `ResolvedSchema`.
- CI, which has its own roadmap item.
- Adding pyrefly. It is a documented fallback, not a deliverable.

## Decisions

### ty replaces mypy
ty is the same family as ruff and uv, handles Pydantic natively (finding 2), checks Streamlit against its real types (finding 3), and was stable on this code across five releases (finding 1).

Fallback: if ty cannot reach zero diagnostics using only the suppression forms below, or its hook proves flaky across two consecutive releases, switch to pyrefly: its default preset, a local `uv run pyrefly check` hook, and the `meta.pyrefly` extension (finding 10).

Alternative: keep mypy. Rejected: its hook ignores missing imports, so it checks Streamlit against nothing, and its Pydantic plugin catches less than ty's built-in rules.

### A local hook runs ty, not the official hook
The hook is a local pre-commit hook running `uv run --all-extras ty check`, with `pass_filenames: false`. `ty` lives in the `dev` group, so `uv.lock` is the only place its version is set and developers and agents run the same ty with `uv run ty` (finding 7). The official hook would give a second version source in its revision and would need `--all-extras` anyway to be deterministic (finding 6).

Consequence: the hook installs the extras into the environment if they are missing. That is harmless and is documented in `AGENTS.md`.

### ty is pinned exactly and gets its own Dependabot group
The dev group pins `ty==0.0.95`. A new group in the `uv` Dependabot ecosystem, listed before the broad `python-minor-and-patch` group, holds only `ty`, so a ty release arrives as its own pull request and cannot block unrelated bumps. The ordering assumes Dependabot places a dependency in the first group it matches; the first Dependabot run after merge confirms it.

Alternative: a bound such as `ty>=0.0.95,<0.1`, rejected because any lock refresh could then pull in new diagnostics unannounced.

### Suppressions are hybrid
This was chosen by you after the evidence in findings 4, 5 and 8.
- **`schema.py`: one scoped override.** `[[tool.ty.overrides]]` for `config_wizard/schema.py` turns off `invalid-mutable-override` and `invalid-attribute-override`. All 19 of its diagnostics share one cause: `ResolvedSchema` subclasses a model and narrows its mutable fields. Redesigning that is a separate change, so the override is the single recorded decision, explained here and in `CONSTITUTION.md` rather than in a config comment.
- **Everything else: inline `# ty: ignore[rule]`.** 16 comments cover the 17 remaining diagnostics (15 lines in `streamlit.py`, where line 265 carries two rules, and 1 in `tests/test_schema.py`). Each names its rule. The Streamlit ones go when `fix-streamlit-collections` and `test-streamlit-backend` land; the test one stays, because it deliberately assigns a wrong type.
- **The 13 mypy-coded comments are deleted**, since ty ignores them (finding 5).

Alternatives: 36 inline comments, 19 of them identical; or refactoring the Streamlit calls now, rejected because that backend has no tests.

### ty checks the maintained directories
The hook runs `ty check` with no paths, which checks every non-ignored Python file in the project, tracked or not, while the other hooks only see tracked files (`pre-commit --all-files` uses `git ls-files`). In a working copy with the untracked, known-broken `test_wizard.py` harness the gate would fail on a file that is not in the repository, and pass on a fresh clone. `[tool.ty.src]` therefore sets `include = ["config_wizard", "scripts", "tests"]`, which is every tracked Python file and the scope the zero-diagnostics result was measured on. It is configuration, not a suppression, and it also governs CLI and editor runs; a new top-level Python directory has to be added to it.

### `unused-ignore-comment` is an error
It replaces mypy's `warn_unused_ignores`, so a suppression cannot outlive its cause. The other `[tool.mypy]` settings need no equivalent: the Pydantic plugin is replaced by ty's built-in rules, and `follow_imports` and `no_implicit_reexport` have no counterpart in use.

### Editor and commands
The devcontainer swaps `ms-python.mypy-type-checker` for `astral-sh.ty`, with no Pylance setting needed (finding 9). `make lint` runs the `ruff-check` and `ty` hook ids. The `.claude/settings.json` permission becomes `uv run ty*`.

## Risks / Trade-offs

- [ty is Beta and releases every few days] -> Pinned exactly and bumped through its own Dependabot group; a release that adds diagnostics fails its own pull request instead of surprising everyone.
- [The hook installs extras into the environment] -> Harmless; documented. A fresh clone is tested end to end.
- [The `schema.py` override could hide a future real override mistake there] -> It names two rules in one file, every other rule still applies to that file, and the redesign that would remove it stays on the roadmap.
- [The editor's ty can differ from the pinned ty] -> The hook is authoritative; a disagreement is resolved by `make lint`.
- [The Dependabot grouping order is an assumption] -> Checked on the first Dependabot run after merge.
- [Inline ignores pile up] -> `unused-ignore-comment` removes stale ones, and the Streamlit ones are tied to named roadmap items.

## Migration Plan

Land as separate commits in dependency order so each can be reverted alone: add `ty` and re-lock, configuration, then the suppressions together with the hook switch and mypy removal in one commit (deleting the mypy-coded ignores turns the mypy hook red until mypy itself is gone), then documents and devcontainer, then Dependabot. The mypy configuration and the dead ignores remain recoverable from git history. Rollback: revert the commits.
