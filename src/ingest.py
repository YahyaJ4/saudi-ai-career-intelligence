"""Document ingestion utilities for the Saudi AI Career Intelligence pipeline."""

from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_core.documents import Document


SUPPORTED_EXTENSIONS = {".pdf", ".txt", ".md"}


def load_document(file_path: str | Path) -> list[Document]:
    """Load a single PDF, text, or Markdown file into LangChain documents."""
    path = Path(file_path)

    if path.suffix.lower() == ".pdf":
        return PyPDFLoader(str(path)).load()

    if path.suffix.lower() in {".txt", ".md"}:
        return TextLoader(str(path), encoding="utf-8").load()

    raise ValueError(f"Unsupported file type: {path.suffix}")


def load_documents(data_dir: str | Path) -> list[Document]:
    """Recursively load supported source files from a data directory."""
    root = Path(data_dir)
    documents: list[Document] = []

    for file_path in root.rglob("*"):
        if file_path.is_file() and file_path.suffix.lower() in SUPPORTED_EXTENSIONS:
            documents.extend(load_document(file_path))

    return documents
