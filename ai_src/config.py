# config.py - Configurações do agente de documentos
# Início da alteração
#
# Variáveis lidas do ambiente (.env ou GitHub Secrets/Variables).
# Valores padrão para desenvolvimento local.

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Caminhos (Paths relativos ao AI_SRC ou absolutos via env)
AI_SRC = Path(__file__).resolve().parent
DATA_DIR = Path(os.getenv("DATA_DIR", str(AI_SRC / "data")))
VECTOR_DB_PATH = Path(os.getenv("VECTOR_DB_PATH", str(DATA_DIR / "chroma_db")))
CONVERSATION_FILE = Path(os.getenv("CONVERSATION_FILE", str(DATA_DIR / "conversation.json")))

# Memória de conversa (últimas N trocas de pergunta/resposta)
MAX_HISTORY_TURNS = int(os.getenv("MAX_HISTORY_TURNS", "5"))

# LLM
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama")  # openai | ollama

# Embeddings (modelo local)
EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL",
    "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
)

# Fim da alteração
