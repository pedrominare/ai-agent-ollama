# main.py - CLI do agente de documentos
# Início da alteração
#
# Use --langchain para rodar com LangChain (padrão: implementação manual)

import sys
from pathlib import Path

# Flags
USE_LANGCHAIN = "--langchain" in sys.argv
if USE_LANGCHAIN:
    sys.argv.remove("--langchain")

USE_REPLACE = "--replace" in sys.argv
if USE_REPLACE:
    sys.argv.remove("--replace")

if USE_LANGCHAIN:
    from agent_langchain import ingestir_documento, responder_pergunta
else:
    from agent import ingestir_documento, responder_pergunta


def main():
    args = sys.argv[1:]
    if not args:
        modo = " (LangChain)" if USE_LANGCHAIN else ""
        print("Uso:")
        print("  python main.py ingest <caminho_arquivo> [--replace] [--langchain]")
        print("  python main.py ask <pergunta> [--langchain]")
        print("  python main.py clear  # limpa memória de conversa")
        print(f"  Modo atual: {'LangChain' if USE_LANGCHAIN else 'manual'}{modo}")
        return

    cmd = args[0].lower()
    if cmd == "clear":
        from memory import clear
        clear()
        print("Memória de conversa limpa.")
        return
    if cmd == "ingest":
        if len(args) < 2:
            print("Informe o caminho do arquivo.")
            return
        caminho = Path(args[1])
        if not caminho.exists():
            print(f"Arquivo não encontrado: {caminho}")
            return
        print(ingestir_documento(caminho, substituir=USE_REPLACE))
    elif cmd == "ask":
        pergunta = " ".join(args[1:]) if len(args) > 1 else ""
        if not pergunta:
            print("Informe a pergunta.")
            return
        print(responder_pergunta(pergunta))
    else:
        print("Comandos: ingest | ask")


if __name__ == "__main__":
    main()

# Fim da alteração
