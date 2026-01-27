"""Pydantic schemas for exam generation."""

from typing import List, Optional
from pydantic import BaseModel, Field


class ExamGenerateSchema(BaseModel):
    """Request schema for exam generation."""

    book_filename: str
    mode: str = Field(pattern="^(chapter)$")
    difficulty: str = Field(default="medium", pattern="^(easy|medium|hard)$")
    chapter_numbers: Optional[List[str]] = None
    topics: Optional[List[str]] = None


class ExamEvaluateSchema(BaseModel):
    """Request schema for open-text answer evaluation."""

    question: str
    expected_answer: str
    user_answer: str
    context: Optional[str] = ""


class ExamEvaluateCodeSchema(BaseModel):
    """Request schema for code-fill evaluation."""

    code: str
    function_name: str
    tests: list
