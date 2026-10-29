#!/usr/bin/env bash
set -euo pipefail

sudo chown vscode:vscode /home/vscode/.claude /home/vscode/.config /home/vscode/.local /home/vscode/.local/share
pipx install uv==0.13.5
uv sync --all-extras
uv run pre-commit install --hook-type pre-commit --hook-type commit-msg
npm install -g @fission-ai/openspec@latest opencode-ai@latest
