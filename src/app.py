"""Streamlit app for the Saudi AI Career Intelligence RAG prototype."""

import streamlit as st
from dotenv import load_dotenv

from retrieval import retrieve_relevant_chunks


def format_sources(chunks) -> str:
    """Create a readable source preview from retrieved chunks."""
    if not chunks:
        return "No relevant chunks found."

    previews = []
    for index, chunk in enumerate(chunks, start=1):
        source = chunk.metadata.get("source", "Unknown source")
        previews.append(f"### Source {index}: {source}\n\n{chunk.page_content[:1000]}")

    return "\n\n".join(previews)


def main() -> None:
    """Run a simple Streamlit interface for querying indexed documents."""
    load_dotenv()

    st.set_page_config(
        page_title="Saudi AI Career Intelligence",
        page_icon="",
        layout="wide",
    )

    st.title("Saudi AI Career Intelligence")
    st.write("Ask questions about Saudi AI careers, Vision 2030, and national strategies.")

    query = st.text_input("Career intelligence question")
    top_k = st.slider("Number of chunks to retrieve", min_value=1, max_value=10, value=5)

    if st.button("Search") and query:
        chunks = retrieve_relevant_chunks(query=query, k=top_k)
        st.markdown(format_sources(chunks))


if __name__ == "__main__":
    main()
