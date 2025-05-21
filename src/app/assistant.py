"""Module for the LLM assistant."""

from typing import Union
from chromadb.api.models.Collection import Collection
from ollama import embed, generate
from .utils import Utils

import sys

class Assistant:
    """Module for the LLM assistant."""

    def __init__(self, embeddings_collection: Union[None, Collection]):
        self.embeddings_collection = embeddings_collection


    def generate_question_embeddings(self, question: str) -> list[str]:
        """."""
        response = embed(
            model = Utils.EMBEDDINGS_MODEL,
            input = question
        )

        results = self.embeddings_collection.query(
            query_embeddings=[response.get("embeddings", "")[0]],
            n_results=Utils.N_DOCUMENTS
        )
        return results['documents']


    def ask(self, question: str):
        """Ask the LLM model a question, the function calls the embeedings db for context."""
        documents = self.generate_question_embeddings(question)
        output = generate(
            model = Utils.CHAT_MODEL,
            prompt = (
                f"Using the following documents from a book: {documents}."
                f"Respond to this question: {question}"
            )
        )
        print(output.get("response", ""))
        print("References: ")
        print(documents)
