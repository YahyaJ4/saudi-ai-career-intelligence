"""Embedding and vector store helpers for the RAG pipeline."""

from pathlib import Path

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings


def get_embedding_model(model_name: str = "text-embedding-3-small") -> OpenAIEmbeddings:
    """Create the OpenAI embedding model used to index and query chunks."""
    return OpenAIEmbeddings(model=model_name)


def create_vector_store(
    chunks: list[Document],
    persist_dir: str | Path = "chroma_db",
    collection_name: str = "saudi_ai_career_sources",
) -> Chroma:
    """Create and persist a Chroma vector store from document chunks."""
    embeddings = get_embedding_model()

    return Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=str(persist_dir),
        collection_name=collection_name,
    )
