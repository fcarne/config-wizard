#!/usr/bin/env bash
set -euo pipefail

sudo chown vscode:vscode /home/vscode/.claude /home/vscode/.config /home/vscode/.local /home/vscode/.local/share
sudo chown -R vscode:nvm "$(npm root -g)/@anthropic-ai"
pipx install uv==0.13.6
uv sync --all-extras
uv run pre-commit install --hook-type pre-commit --hook-type commit-msg
npm install -g @fission-ai/openspec@1.15.0 opencode-ai@latest
git config --global alias.prune-gone '!f() { git fetch -p || return; cur=$(git symbolic-ref --short -q HEAD); git for-each-ref --format="%(refname:short) %(objectname:short) %(upstream:track)" refs/heads | while read -r b sha t; do [ "$t" = "[gone]" ] || continue; if [ "$b" = "$cur" ]; then echo "skipped $b (checked out)"; else git branch -D "$b" >/dev/null && echo "deleted $b (was $sha; restore with: git branch $b $sha)"; fi; done; }; f'
