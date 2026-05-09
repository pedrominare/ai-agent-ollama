#!/usr/bin/env bash
# BEGIN: run_debug_agent.sh - espelha .vscode/launch.json no Linux (cwd ai_src, mesmos perfis).
# Uso via subprocess Python (ex.):
#   subprocess.run(
#       ["bash", str(REPO / "run_debug_agent.sh"), "--workspace", str(REPO), "ask", "Sua pergunta?"],
#       check=True,
#       cwd=str(REPO),
#   )
# Perfis: ask | ask-langchain | ingest | ingest-langchain | ingest-replace | clear | main
# Flags antes do perfil: --no-ollama  |  --workspace DIR
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "${RUN_DEBUG_AGENT_ROOT:-$SCRIPT_DIR}" && pwd)"
OLLAMA_PRE=1
PYTHON="${PYTHON:-python3}"

DEFAULT_ASK_QUESTION="Qual é a função do conselho deliberativo?"
DEFAULT_ASK_LANGCHAIN_QUESTION="O Diretor Tesoureiro tem quais atribuições? Os balancetes são de sua responsabilidade?"

show_help() {
    cat <<'EOF'
run_debug_agent.sh [flags globais] <perfil> [argumentos do perfil]

Flags globais (antes do perfil):
  --workspace DIR   raiz do repo (padrao: diretorio deste script)
  --no-ollama       nao executa .vscode/ensure-ollama.sh

Perfis (equivalentes ao launch.json):
  ask [pergunta...]              modo manual; pergunta padrao se omitida
  ask-langchain [pergunta...]    com --langchain
  ingest [arquivo]               padrao: BACKUP DO ESTATUTO SOCIAL.pdf na raiz do repo
  ingest-langchain [arquivo]
  ingest-replace [arquivo]       padrao: arquivo.xlsx na raiz do repo
  clear
  main                           python main.py sem args (imprime uso interno)

Variaveis opcionais:
  RUN_DEBUG_AGENT_ROOT, PYTHON, DEFAULT_INGEST_PDF, DEFAULT_INGEST_REPLACE_XLSX
EOF
}

ensure_ollama() {
    if [[ "$OLLAMA_PRE" -eq 1 ]]; then
        bash "$ROOT/.vscode/ensure-ollama.sh"
    fi
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --no-ollama)
            OLLAMA_PRE=0
            shift
            ;;
        --workspace)
            ROOT="$(cd "$2" && pwd)"
            shift 2
            ;;
        --workspace=*)
            ROOT="$(cd "${1#*=}" && pwd)"
            shift
            ;;
        -h | --help | help)
            show_help
            exit 0
            ;;
        *)
            break
            ;;
    esac
done

DEFAULT_INGEST_PDF="${DEFAULT_INGEST_PDF:-$ROOT/BACKUP DO ESTATUTO SOCIAL.pdf}"
DEFAULT_INGEST_REPLACE_XLSX="${DEFAULT_INGEST_REPLACE_XLSX:-$ROOT/arquivo.xlsx}"

AI_SRC="$ROOT/ai_src"
if [[ ! -d "$AI_SRC" ]]; then
    echo "Diretorio ai_src nao encontrado em: $ROOT" >&2
    exit 1
fi
cd "$AI_SRC"

PROFILE="${1:-}"
if [[ -z "$PROFILE" ]]; then
    echo "Informe um perfil. Use: $0 help" >&2
    exit 1
fi
shift || true

case "$PROFILE" in
    ask)
        ensure_ollama
        if [[ $# -gt 0 ]]; then
            Q="$*"
        else
            Q="$DEFAULT_ASK_QUESTION"
        fi
        "$PYTHON" main.py ask "$Q"
        ;;
    ask-langchain)
        ensure_ollama
        if [[ $# -gt 0 ]]; then
            Q="$*"
        else
            Q="$DEFAULT_ASK_LANGCHAIN_QUESTION"
        fi
        "$PYTHON" main.py ask "$Q" --langchain
        ;;
    ingest)
        FILE="${1:-$DEFAULT_INGEST_PDF}"
        if [[ ! -f "$FILE" ]]; then
            echo "Arquivo nao encontrado: $FILE" >&2
            exit 1
        fi
        "$PYTHON" main.py ingest "$FILE"
        ;;
    ingest-langchain)
        FILE="${1:-$DEFAULT_INGEST_PDF}"
        if [[ ! -f "$FILE" ]]; then
            echo "Arquivo nao encontrado: $FILE" >&2
            exit 1
        fi
        "$PYTHON" main.py ingest "$FILE" --langchain
        ;;
    ingest-replace)
        FILE="${1:-$DEFAULT_INGEST_REPLACE_XLSX}"
        if [[ ! -f "$FILE" ]]; then
            echo "Arquivo nao encontrado: $FILE" >&2
            exit 1
        fi
        "$PYTHON" main.py ingest "$FILE" --replace
        ;;
    clear)
        "$PYTHON" main.py clear
        ;;
    main | usage)
        ensure_ollama
        "$PYTHON" main.py
        ;;
    *)
        echo "Perfil desconhecido: $PROFILE. Use: $0 help" >&2
        exit 1
        ;;
esac
# END: run_debug_agent.sh
