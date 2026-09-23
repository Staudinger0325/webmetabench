#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
RUNTIME="${RUNTIME_DIR:-$ROOT/.runtime}"
mkdir -p "$RUNTIME"
python3 -m venv "$RUNTIME/python"
"$RUNTIME/python/bin/python" -m pip install --upgrade pip
LITELLM_SPEC=litellm
if [[ "${LITELLM_VERSION:-latest}" != latest ]]; then
  LITELLM_SPEC="litellm==$LITELLM_VERSION"
fi
"$RUNTIME/python/bin/python" -m pip install "$LITELLM_SPEC" openai tqdm
npm install --prefix "$RUNTIME/node" --no-save \
  "@anthropic-ai/claude-code@${CLAUDE_CODE_VERSION:-latest}" \
  "@openai/codex@${CODEX_VERSION:-latest}" \
  "playwright-core@${PLAYWRIGHT_VERSION:-latest}" \
  "@modelcontextprotocol/sdk@${MCP_SDK_VERSION:-latest}" zod@latest
{
  "$RUNTIME/node/node_modules/.bin/claude" --version
  "$RUNTIME/node/node_modules/.bin/codex" --version
  "$RUNTIME/python/bin/python" -m pip freeze
  npm list --prefix "$RUNTIME/node" --depth=0 || true
} > "$RUNTIME/installed-versions.txt"
printf 'Installed runtime: %s\nVersions: %s/installed-versions.txt\n' "$RUNTIME" "$RUNTIME"
printf 'CLI directory: %s/node/node_modules/.bin\n' "$RUNTIME"

