"""Retrieval helpers for finding source chunks relevant to a user query."""

from pathlib import Path

from langchain_chroma import Chroma
from langchain_core.documents import Document

from embeddings import get_embedding_model


def load_vector_store(
    persist_dir: str | Path = "chroma_db",
    collection_name: str = "saudi_ai_career_sources",
) -> Chroma:
    """Load an existing Chroma vector store for retrieval."""
    return Chroma(
        persist_directory=str(persist_dir),
        collection_name=collection_name,
        embedding_function=get_embedding_model(),
    )


def retrieve_relevant_chunks(
    query: str,
    persist_dir: str | Path = "chroma_db",
    collection_name: str = "saudi_ai_career_sources",
    k: int = 5,
) -> list[Document]:
    """Search the vector store and return the most relevant chunks."""
    vector_store = load_vector_store(
        persist_dir=persist_dir,
        collection_name=collection_name,
    )

    return vector_store.similarity_search(query, k=k)
