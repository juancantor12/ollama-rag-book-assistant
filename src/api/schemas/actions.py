"""Pydantic basemodel for a question."""

from pydantic import BaseModel


class AskSchema(BaseModel):
    """Pydantic basemodel for a question."""

    question: str
    book_filename: str


class GenerateEmbeddingsSchema(BaseModel):
    """Pydantic basemodel for a question."""

    book_filename: str
