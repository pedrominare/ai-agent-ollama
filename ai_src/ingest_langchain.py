# ingest_langchain.py - Document Loaders do LangChain
# Início da alteração
#
# CONCEITO: LangChain usa "Document Loaders" para carregar arquivos.
# Cada loader retorna uma lista de Document(page_content, metadata).
# O formato Document é padrão em todo o ecossistema LangChain.

from pathlib import Path
from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader

# Nosso ingest original para Excel/Word (LangChain não tem loader nativo leve para Excel)
from ingest import extrair_texto


def carregar_documento(caminho: Path) -> list[Document]:
    """
    Carrega documento e retorna lista de Document (formato LangChain).
    - PDF: PyPDFLoader (loader oficial)
    - Excel/Word: nosso ingest + conversão para Document
    """
    suf = caminho.suffix.lower()
    nome = caminho.name

    if suf == ".pdf":
        # PyPDFLoader: cada página vira um Document
        loader = PyPDFLoader(str(caminho))
        docs = loader.load()
        # Adiciona metadata com nome do arquivo
        for d in docs:
            d.metadata["source"] = nome
        return docs

    if suf in (".xlsx", ".xls") or suf == ".docx":
        # Usa nosso extractor e converte para Document
        texto, _ = extrair_texto(caminho)
        if not texto.strip():
            return []
        return [Document(page_content=texto, metadata={"source": nome})]

    raise ValueError(f"Formato não suportado: {suf}")

# Fim da alteração
