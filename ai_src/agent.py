# agent.py - Agente RAG: ingestão e respostas
# Início da alteração

from pathlib import Path

from config import VECTOR_DB_PATH, EMBEDDING_MODEL, LLM_PROVIDER, OPENAI_API_KEY
from ingest import extrair_texto
from memory import add_turn, get_history_messages
from vector_store import criar_cliente, obter_embeddings, dividir_texto, deletar_documento


def ingestir_documento(caminho: Path, substituir: bool = False) -> str:
    """
    Extrai texto do documento, gera embeddings e armazena na base vetorial.
    substituir=True: remove versão anterior do mesmo arquivo (manutenção rara).
    Padrão: adiciona (acumula mês a mês).
    """
    texto, nome = extrair_texto(caminho)
    chunks = dividir_texto(texto)
    if not chunks:
        return f"Nenhum texto extraído de {nome}"

    client = criar_cliente(VECTOR_DB_PATH)
    collection = client.get_or_create_collection("documentos", metadata={"hnsw:space": "cosine"})

    if substituir:
        deletar_documento(VECTOR_DB_PATH, "documentos", nome, metadata_key="doc")

    embeddings = obter_embeddings(chunks, EMBEDDING_MODEL)
    ids = [f"{nome}_{i}" for i in range(len(chunks))]
    metadatas = [{"doc": nome, "chunk": i} for i in range(len(chunks))]

    collection.add(ids=ids, embeddings=embeddings, documents=chunks, metadatas=metadatas)
    acao = "Substituído" if substituir else "Ingerido"
    return f"{acao}: {nome} ({len(chunks)} chunks)"


def responder_pergunta(pergunta: str, top_k: int = 5) -> str:
    """
    Busca contexto na base vetorial e gera resposta via LLM.
    """
    client = criar_cliente(VECTOR_DB_PATH)
    collection = client.get_or_create_collection("documentos", metadata={"hnsw:space": "cosine"})

    if collection.count() == 0:
        return "Nenhum documento foi ingerido ainda. Use 'ingestir' para adicionar documentos."

    # Embedding da pergunta
    q_emb = obter_embeddings([pergunta], EMBEDDING_MODEL)[0]

    # Busca semântica
    results = collection.query(query_embeddings=[q_emb], n_results=top_k, include=["documents", "metadatas"])
    docs = results["documents"][0] or []
    contexto = "\n\n---\n\n".join(docs)

    # Chamar LLM (com histórico de conversa)
    if LLM_PROVIDER == "openai" and OPENAI_API_KEY:
        resposta = _resposta_openai(pergunta, contexto)
    else:
        resposta = _resposta_ollama(pergunta, contexto)

    add_turn(pergunta, resposta)
    return resposta


def _build_messages(pergunta: str, contexto: str) -> list[dict]:
    """Monta mensagens: system + histórico + pergunta atual com contexto."""
    # Início da alteração: resposta no mesmo idioma da pergunta (evita PT fixo com pergunta em EN).
    system = (
        "Responda com base APENAS no contexto fornecido. Use o histórico da conversa para entender referências "
        "(ex: 'e em relação a X?'). Se não houver informação, diga que não encontrou. "
        "Use o mesmo idioma da pergunta atual: inglês se a pergunta for em inglês, português se for em português."
    )
    # Fim da alteração: resposta no mesmo idioma da pergunta
    user_content = f"Contexto dos documentos:\n{contexto}\n\nPergunta atual: {pergunta}"
    messages = [{"role": "system", "content": system}]
    messages.extend(get_history_messages())
    messages.append({"role": "user", "content": user_content})
    return messages


def _resposta_openai(pergunta: str, contexto: str) -> str:
    from openai import OpenAI
    client = OpenAI()
    messages = _build_messages(pergunta, contexto)
    # Não incluir a resposta atual no histórico antes de chamar (add_turn é depois)
    # O histórico já tem as perguntas/respostas anteriores
    resp = client.chat.completions.create(model="gpt-4o-mini", messages=messages)
    return resp.choices[0].message.content


def _resposta_ollama(pergunta: str, contexto: str) -> str:
    try:
        from openai import OpenAI
        client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")
        messages = _build_messages(pergunta, contexto)
        resp = client.chat.completions.create(model="mistral", messages=messages)
        return resp.choices[0].message.content
    except Exception as e:
        return f"Erro ao chamar Ollama (verifique se está rodando): {e}"

# Fim da alteração
