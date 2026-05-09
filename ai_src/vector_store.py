# vector_store.py - Base vetorial persistente (ChromaDB)
# Início da alteração

from pathlib import Path
from typing import Optional

import chromadb
from chromadb.config import Settings


def criar_cliente(persist_path: Path):
    """Cria cliente ChromaDB com persistência em disco."""
    persist_path.mkdir(parents=True, exist_ok=True)
    return chromadb.PersistentClient(
        path=str(persist_path),
        settings=Settings(anonymized_telemetry=False),
    )


def obter_embeddings(textos: list[str], model_name: str) -> list[list[float]]:
    """Gera embeddings com sentence-transformers."""
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer(model_name)
    return model.encode(textos).tolist()


def dividir_texto(texto: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    """Divide texto em chunks para embedding."""
    chunks = []
    start = 0
    while start < len(texto):
        fim = start + chunk_size
        chunk = texto[start:fim]
        if chunk.strip():
            chunks.append(chunk)
        start = fim - overlap
    return chunks


def deletar_documento(persist_path: Path, collection_name: str, doc_name: str, metadata_key: str = "doc") -> None:
    """
    Remove da base vetorial todos os chunks de um documento.
    Se a collection não existir, ignora (nada a remover).
    """
    client = criar_cliente(persist_path)
    try:
        collection = client.get_collection(collection_name)
        collection.delete(where={metadata_key: {"$eq": doc_name}})
    except Exception:
        pass  # collection inexistente ou doc não encontrado

# Fim da alteração
