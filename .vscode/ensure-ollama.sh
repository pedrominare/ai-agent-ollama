#!/usr/bin/env bash
# BEGIN: Garantir Ollama ativo para preLaunchTask do VS Code/Cursor
set -e
URI="http://127.0.0.1:11434/"
if curl -sf "$URI" >/dev/null; then
  exit 0
fi
if ! command -v ollama >/dev/null 2>&1; then
  echo "ollama nao encontrado no PATH. Instale: https://ollama.com/download" >&2
  exit 1
fi
nohup ollama serve >/dev/null 2>&1 &
for _ in $(seq 1 120); do
  if curl -sf "$URI" >/dev/null; then
    exit 0
  fi
  sleep 0.5
done
echo "Ollama nao respondeu em ${URI} apos ~60s." >&2
exit 1
# END: Garantir Ollama ativo
