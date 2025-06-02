"""Module for the LLM assistant."""

from typing import List, Union
from chromadb.api.models.Collection import Collection
from ollama import embed, generate
import pymupdf
from .utils import Utils


class Assistant:
    """Module for the LLM assistant."""

    def __init__(
        self, book_filename: str, embeddings_collection: Union[None, Collection]
    ):
        self.book_filename = book_filename
        self.embeddings_collection = embeddings_collection
        self.book = pymupdf.open(f"{Utils.get_data_path()}/{self.book_filename}")

    def get_rag_documents(self, question: str) -> List[str]:
        """Retrieve related document references from the vectordb and pull related pages from the book."""
        response = embed(model=Utils.EMBEDDINGS_MODEL, input=question)
        results = self.embeddings_collection.query(
            query_embeddings=response.get("embeddings", ""),
            n_results=Utils.N_DOCUMENTS,
        )
        rag_documents = ""
        pages = set()
        references = set()
        for metadata in results["metadatas"][0]:
            page = metadata["page"]
            if page not in pages:
                surrounding_pages = [page - 1, page, page + 1]
                reference = f"From {metadata["title"]} (pages {', '.join([str(pg + 1) for pg in surrounding_pages])})"
                for surrounding_page in surrounding_pages:
                    pages.add(surrounding_page)
                    rag_documents += (
                        f"\n{metadata['title']}, page {surrounding_page}: "
                        f"\n{self.book.load_page(surrounding_page).get_text()}\n"
                    )
                references.add(reference)
        return rag_documents, references

    def ask(self, question: str) -> dict:
        """Ask the LLM model a question, the function calls the embeedings db for context."""
        rag_documents, references = self.get_rag_documents(question)
        output = generate(
            model=Utils.CHAT_MODEL,
            prompt=(
                f"The user will make a question about the book {self.book.metadata.get('title', '')}"
                f"from the authors: {self.book.metadata.get('author', '')}"
                "The RAG system indentified a related page from the book."
                f"These are previou, actual page and next page from the book to provide context: {rag_documents}."
                f"Based on those pages respond to this user question: {question}"
            ),
        )
        return {"answer": output.get("response", ""), "references": references}
