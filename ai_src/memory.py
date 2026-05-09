# memory.py - Memória de conversa persistente
# Início da alteração
#
# Armazena histórico de perguntas e respostas em arquivo JSON.
# Usado para dar contexto ao agente (ex: "E em relação a abril?").

import json
from pathlib import Path
from typing import Optional

from config import CONVERSATION_FILE, MAX_HISTORY_TURNS


def _load() -> list[dict]:
    """Carrega histórico do arquivo."""
    if not CONVERSATION_FILE.exists():
        return []
    try:
        with open(CONVERSATION_FILE, encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return []


def _save(messages: list[dict]) -> None:
    """Salva histórico no arquivo."""
    CONVERSATION_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(CONVERSATION_FILE, "w", encoding="utf-8") as f:
        json.dump(messages, f, ensure_ascii=False, indent=2)


def add_turn(pergunta: str, resposta: str) -> None:
    """Adiciona uma pergunta e resposta ao histórico."""
    messages = _load()
    messages.append({"role": "user", "content": pergunta})
    messages.append({"role": "assistant", "content": resposta})
    # Mantém apenas os últimos N turnos (cada turno = 2 mensagens)
    max_msgs = MAX_HISTORY_TURNS * 2
    if len(messages) > max_msgs:
        messages = messages[-max_msgs:]
    _save(messages)


def get_history_messages() -> list[dict]:
    """Retorna mensagens formatadas para o LLM (role + content)."""
    return _load()


def clear() -> None:
    """Limpa o histórico de conversa."""
    if CONVERSATION_FILE.exists():
        CONVERSATION_FILE.unlink()

# Fim da alteração
