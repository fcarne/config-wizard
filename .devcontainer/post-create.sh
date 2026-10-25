#!/usr/bin/env bash
set -euo pipefail

sudo chown vscode:vscode /home/vscode/.claude /home/vscode/.config /home/vscode/.local /home/vscode/.local/share
poetry install --all-extras
pipx install pre-commit
pre-commit install
npm install -g @fission-ai/openspec@latest opencode-ai@latest
