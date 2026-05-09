# agent_langchain.py - Agente RAG com LangChain
# Início da alteração
#
# CONCEITOS LANGCHAIN:
# 1. Document Loaders -> carregam arquivos em Document
# 2. Text Splitter -> divide em chunks
# 3. Embeddings -> vetorizam o texto
# 4. Vector Store -> armazena e busca por similaridade
# 5. Retriever -> interface de busca
# 6. Chain -> orquestra: pergunta -> retriever -> LLM -> resposta

from pathlib import Path

from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from config import VECTOR_DB_PATH, EMBEDDING_MODEL, LLM_PROVIDER, OPENAI_API_KEY
from ingest_langchain import carregar_documento
from memory import add_turn, get_history_messages

# Nome da collection (separada da versão manual para não conflitar)
COLLECTION_NAME = "documentos_langchain"


def _get_embeddings():
    """Embeddings locais via HuggingFace (sentence-transformers)."""
    return HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={"device": "cpu"},
    )


def _get_llm():
    """Retorna o LLM configurado (OpenAI ou Ollama)."""
    if LLM_PROVIDER == "openai" and OPENAI_API_KEY:
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(model="gpt-4o-mini", temperature=0)
    from langchain_ollama import ChatOllama
    return ChatOllama(model="mistral", temperature=0)


def _get_vector_store():
    """Chroma persistente com embeddings."""
    VECTOR_DB_PATH.mkdir(parents=True, exist_ok=True)
    return Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=_get_embeddings(),
        persist_directory=str(VECTOR_DB_PATH),
    )


def ingestir_documento(caminho: Path, substituir: bool = False) -> str:
    """
    Ingestão com LangChain.
    substituir=True: remove versão anterior do mesmo arquivo (manutenção rara).
    Padrão: adiciona (acumula mês a mês).
    """
    from vector_store import deletar_documento

    docs = carregar_documento(caminho)
    if not docs:
        return f"Nenhum texto extraído de {caminho.name}"

    nome = caminho.name

    if substituir:
        deletar_documento(VECTOR_DB_PATH, COLLECTION_NAME, nome, metadata_key="source")

    # Text Splitter: divide em chunks com overlap
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        separators=["\n\n", "\n", " ", ""],
    )
    chunks = splitter.split_documents(docs)

    # Chroma: add_documents faz embed + persist automaticamente
    vector_store = _get_vector_store()
    vector_store.add_documents(chunks)

    acao = "Substituído" if substituir else "Ingerido"
    return f"{acao} (LangChain): {nome} ({len(chunks)} chunks)"


def responder_pergunta(pergunta: str, top_k: int = 5) -> str:
    """
    RAG com LangChain + memória de conversa:
    Retriever -> contexto + histórico -> LLM -> Resposta
    """
    vector_store = _get_vector_store()
    retriever = vector_store.as_retriever(search_kwargs={"k": top_k})
    docs = retriever.invoke(pergunta)
    contexto = "\n\n---\n\n".join(d.page_content for d in docs) if docs else ""

    # Monta mensagens com histórico (igual ao agent manual)
    # Início da alteração: resposta no mesmo idioma da pergunta (evita PT fixo com pergunta em EN).
    system = (
        "Responda com base APENAS no contexto fornecido. Use o histórico da conversa para entender referências. "
        "Se não houver informação, diga que não encontrou. "
        "Use o mesmo idioma da pergunta atual: inglês se a pergunta for em inglês, português se for em português."
    )
    # Fim da alteração: resposta no mesmo idioma da pergunta
    user_content = f"Contexto dos documentos:\n{contexto}\n\nPergunta atual: {pergunta}"

    from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
    messages = [SystemMessage(content=system)]
    for m in get_history_messages():
        if m["role"] == "user":
            messages.append(HumanMessage(content=m["content"]))
        else:
            messages.append(AIMessage(content=m["content"]))
    messages.append(HumanMessage(content=user_content))

    llm = _get_llm()
    resposta = llm.invoke(messages).content
    add_turn(pergunta, resposta)
    return resposta

# Fim da alteração
