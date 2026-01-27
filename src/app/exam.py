"""Exam generation utilities."""

from __future__ import annotations

import json
import re
from datetime import datetime
from typing import Dict, List, Optional
from uuid import uuid4

import requests
import pymupdf

from app.utils import Utils


class ExamGenerator:
    """Generates ephemeral exams from indexed topics and embeddings."""

    def __init__(self, book_filename: str):
        self.book_filename = book_filename
        self.output_folder = Utils.strip_extension(book_filename)

    @staticmethod
    def _safe_text(value: object) -> str:
        text = str(value) if value is not None else ""
        return (
            text.encode("utf-8", "replace")
            .decode("utf-8")
            .replace("?", "")
            .strip()
        )

    @staticmethod
    def _clean_page_text(text: str) -> str:
        """Remove TOC-like/bibliography noise from page text."""
        cleaned_lines = []
        for line in text.splitlines():
            stripped = line.strip()
            if not stripped:
                continue
            lower = stripped.lower()
            if lower in {"contents", "summary", "bibliographical and historical notes"}:
                continue
            dot_ratio = stripped.count(".") / max(len(stripped), 1)
            if dot_ratio > 0.25:
                continue
            if re.match(r"^\d+(\.\d+)*\s+.*\.+\s+\d+$", stripped):
                continue
            cleaned_lines.append(stripped)
        return "\n".join(cleaned_lines)

    def _get_toc(self) -> List[dict]:
        toc_entries = []
        with pymupdf.open(f"{Utils.get_data_path()}/{self.book_filename}") as book:
            page_count = book.page_count
            toc = [(lvl, title, page) for lvl, title, page in book.get_toc() if page >= 0]
        if not toc:
            return toc_entries
        for idx, (level, title, page_start) in enumerate(toc):
            page_end = page_count - 1
            for j in range(idx + 1, len(toc)):
                next_level, _next_title, next_page = toc[j]
                if next_level <= level:
                    page_end = max(next_page - 1, page_start)
                    break
            toc_entries.append(
                {
                    "number": str(idx + 1),
                    "title": self._safe_text(title),
                    "level": int(level),
                    "page_start": int(page_start),
                    "page_end": int(page_end),
                }
            )
        return toc_entries

    def get_options(self) -> dict:
        return {"chapters": self._get_toc()}

    def generate_exam(
        self,
        mode: str,
        difficulty: str = "medium",
        chapter_numbers: Optional[List[str]] = None,
        topics: Optional[List[str]] = None,
    ) -> dict:
        if mode != "chapter":
            raise ValueError("mode must be 'chapter'")

        # Derive question count from chapter length: ~1 per 3 pages.
        toc_entries = self._get_toc()
        chapter_numbers = chapter_numbers or []
        if not chapter_numbers:
            raise ValueError("No chapter selected.")
        selected = None
        for entry in toc_entries:
            if entry["number"] == chapter_numbers[0]:
                selected = entry
                break
        if not selected:
            raise ValueError("Selected chapter not found.")

        page_span = max(1, selected["page_end"] - selected["page_start"] + 1)
        question_count = max(1, page_span // 3)
        question_count = min(question_count, Utils.EXAM_MAX_QUESTIONS)

        chapter_text = self._extract_chapter_text(
            page_start=selected["page_start"],
            page_end=selected["page_end"],
        )
        if not chapter_text:
            raise ValueError("No text found for selected chapter.")

        chunks = self._chunk_text_by_count(chapter_text, parts=question_count)
        questions = []
        prompts = []
        for idx, chunk in enumerate(chunks):
            selected_type = self._select_question_type(chunk, difficulty)
            prompt = self._build_prompt(
                question_count=1,
                difficulty=difficulty,
                context_text=chunk,
                forced_type=selected_type,
            )
            prompts.append(prompt)
            Utils.logger.warning("Exam prompt: %s", self._safe_text(prompt))
            response = requests.post(
                Utils.OLLAMA_URL + "/generate",
                json={
                    "model": Utils.CHAT_MODEL,
                    "options": {"temperature": 0.2},
                    "stream": False,
                    "prompt": prompt,
                },
                timeout=300,
            )
            raw = response.json().get("response", "").strip()
            Utils.logger.warning("Exam raw response: %s", self._safe_text(raw))
            data = self._extract_questions_from_raw(raw)
            if not data:
                safe_raw = self._safe_text(raw)
                Utils.logger.warning(
                    "Exam generation returned invalid JSON. Raw response: %s",
                    safe_raw,
                )
                Utils.logger.warning("Parsed payload: %s", data)
                continue
            if "questions" in data and isinstance(data.get("questions"), list):
                normalized = self._normalize_questions(data.get("questions", []))
            else:
                normalized = self._normalize_questions([data])
            if normalized:
                question = normalized[0]
                if question.get("type") != selected_type:
                    question["type"] = selected_type
                questions.append(question)

        if not questions:
            raise ValueError("Failed to generate a valid exam payload.")

        for question in questions:
            question["sources"] = [
                {
                    "section": selected["title"],
                    "pages": list(range(selected["page_start"], selected["page_end"] + 1)),
                }
            ]
            question["context"] = chapter_text

        return {
            "exam_id": str(uuid4()),
            "book_filename": self.book_filename,
            "mode": mode,
            "chapter": selected,
            "question_count": question_count,
            "created_at": datetime.utcnow().isoformat() + "Z",
            "prompts": prompts,
            "questions": questions,
        }

    @staticmethod
    def evaluate_open_text(
        question: str,
        expected_answer: str,
        user_answer: str,
        context: str = "",
    ) -> dict:
        prompt = (
            "You are grading an open-text answer.\n"
            "Return JSON only with keys: status, feedback.\n"
            "status must be one of: correct, incorrect, needs_more.\n"
            "Use the context if provided.\n"
            "Question:\n"
            f"{question}\n\n"
            "Expected answer:\n"
            f"{expected_answer}\n\n"
            "User answer:\n"
            f"{user_answer}\n\n"
            "Context:\n"
            f"{context}"
        )
        response = requests.post(
            Utils.OLLAMA_URL + "/generate",
            json={
                "model": Utils.CHAT_MODEL,
                "options": {"temperature": 0},
                "stream": False,
                "prompt": prompt,
            },
            timeout=180,
        )
        raw = response.json().get("response", "").strip()
        data = ExamGenerator._safe_json(raw) or {}
        status = str(data.get("status", "incorrect")).strip().lower()
        if status not in {"correct", "incorrect", "needs_more"}:
            status = "incorrect"
        feedback = str(data.get("feedback", "")).strip()
        return {"status": status, "feedback": feedback}

    @staticmethod
    def _build_prompt(
        question_count: int,
        difficulty: str,
        context_text: str,
        forced_type: str,
    ) -> str:
        return (
            "Please take a look at this pages:\n"
            f"{context_text}\n"
            "You are an exam generator. Do NOT summarize the text.\n"
            "Your only task is to output JSON that matches the schema below.\n"
            "Generate exactly ONE question.\n"
            f"Difficulty: {difficulty}.\n"
            "Make questions more complex and use longer answer options.\n"
            f"Use question type: {forced_type}.\n"
            "Allowed types: 'multiple_choice', 'open_text', or 'code_fill'.\n"
            "Ensure the output matches the requested question type.\n"
            "Return ONLY JSON. No markdown, no code fences, no commentary.\n"
            "Ensure the JSON format is respected exactly.\n"
            "If you cannot comply, return an empty JSON object: {}.\n"
            "For code_prompt, use a normal JSON string in double quotes. "
            "Do not use triple quotes. Use single quotes inside the code if needed.\n"
            "All fields must be JSON-serializable. Tests must NOT include functions/lambdas. "
            "Use only plain numbers, strings, booleans, arrays, and objects.\n"
            "Use a single JSON object with this schema:\n"
            "{\n"
            '  "id": "q1",\n'
            '  "type": "multiple_choice",\n'
            '  "question": "question text",\n'
            '  "choices": ["A", "B", "C", "D"],\n'
            '  "answer_index": 0,\n'
            '  "expected_answer": "short expected answer for open_text",\n'
            '  "code_prompt": "python code with TODOs for code_fill",\n'
            '  "function_name": "function to call for tests",\n'
            '  "tests": [{"input": [1,2,3], "output": 6}],\n'
            '  "hint": "short hint for a wrong answer",\n'
            '  "explanation": "short explanation of the correct answer"\n'
            "}\n"
        )

    @staticmethod
    def _safe_json(raw: str) -> Optional[Dict[str, object]]:
        if not raw:
            return None
        start = raw.find("{")
        end = raw.rfind("}")
        if start == -1 or end == -1 or end <= start:
            return None
        try:
            return json.loads(raw[start : end + 1])
        except json.JSONDecodeError:
            return None

    @classmethod
    def _extract_questions_from_raw(cls, raw: str) -> Optional[Dict[str, object]]:
        """Try to recover question objects from messy model output."""
        data = cls._safe_json(raw)
        if data and isinstance(data.get("questions", None), list):
            return data
        if data and "question" in data:
            return data
        if "```" in raw:
            fence_blocks = re.findall(r"```(?:json)?\\s*([\\s\\S]*?)```", raw, re.IGNORECASE)
            for block in fence_blocks:
                data = cls._safe_json(block.strip())
                if data and isinstance(data.get("questions", None), list):
                    return data
                if data and "question" in data:
                    return data
        # Strip common markdown fences
        cleaned = raw.replace("```json", "```").replace("```", "")
        data = cls._safe_json(cleaned)
        if data and isinstance(data.get("questions", None), list):
            return data
        if data and "question" in data:
            return data
        # Fallback: extract multiple JSON objects and wrap as questions list
        questions = []
        buf = []
        depth = 0
        for ch in cleaned:
            if ch == "{":
                depth += 1
            if depth > 0:
                buf.append(ch)
            if ch == "}":
                depth -= 1
                if depth == 0 and buf:
                    block = "".join(buf)
                    buf = []
                    try:
                        obj = json.loads(block)
                        if isinstance(obj, dict):
                            questions.append(obj)
                    except json.JSONDecodeError:
                        continue
        if questions:
            return {"questions": questions}
        return None

    @staticmethod
    def _normalize_questions(
        questions: List[dict]
    ) -> List[dict]:
        normalized: List[dict] = []
        for idx, question in enumerate(questions):
            if not isinstance(question, dict):
                continue
            q_type = str(question.get("type", "multiple_choice")).strip().lower()
            if q_type not in {"multiple_choice", "open_text", "code_fill"}:
                q_type = "multiple_choice"
            q_text = str(question.get("question", "")).strip()
            choices = question.get("choices", [])
            answer_index = question.get("answer_index", None)
            hint = str(question.get("hint", "")).strip()
            explanation = str(question.get("explanation", "")).strip()
            expected_answer = str(question.get("expected_answer", "")).strip()
            code_prompt = str(question.get("code_prompt", "")).strip()
            function_name = str(question.get("function_name", "")).strip()
            tests = question.get("tests", [])
            if not q_text:
                continue
            if q_type == "multiple_choice":
                if not isinstance(choices, list) or len(choices) < 4:
                    continue
                if not isinstance(answer_index, int) or answer_index not in range(4):
                    continue
            if q_type == "open_text" and not expected_answer:
                continue
            if q_type == "code_fill":
                if not code_prompt or not function_name or not isinstance(tests, list) or not tests:
                    continue
            normalized.append(
                {
                    "id": question.get("id") or f"q{idx+1}",
                    "type": q_type,
                    "question": q_text,
                    "choices": [str(choice) for choice in choices[:4]] if isinstance(choices, list) else [],
                    "answer_index": answer_index if isinstance(answer_index, int) else None,
                    "expected_answer": expected_answer,
                    "code_prompt": code_prompt,
                    "function_name": function_name,
                    "tests": tests if isinstance(tests, list) else [],
                    "hint": hint,
                    "explanation": explanation,
                }
            )
        return normalized

    def _select_question_type(self, context_text: str, difficulty: str) -> str:
        prompt = (
            "Choose the best question type for this context.\n"
            "Return only one of: multiple_choice, open_text, code_fill.\n"
            "Use code_fill only if the context contains algorithms or step-by-step procedures.\n"
            f"Context:\n{context_text[:1500]}"
        )
        try:
            response = requests.post(
                Utils.OLLAMA_URL + "/generate",
                json={
                    "model": Utils.CHAT_MODEL,
                    "options": {"temperature": 0},
                    "stream": False,
                    "prompt": prompt,
                },
                timeout=60,
            )
            raw = response.json().get("response", "").strip().lower()
            if "code" in raw:
                return "code_fill"
            if "open" in raw:
                return "open_text"
            if "multiple" in raw:
                return "multiple_choice"
        except Exception:
            pass
        return "multiple_choice"

    def _extract_chapter_text(self, page_start: int, page_end: int) -> str:
        texts = []
        with pymupdf.open(f"{Utils.get_data_path()}/{self.book_filename}") as book:
            for page in range(page_start, page_end + 1):
                try:
                    page_text = book.load_page(page).get_text()
                    if page_text:
                        texts.append(page_text)
                except Exception:
                    continue
        return "\n\n".join(texts)

    @staticmethod
    def _chunk_text(text: str, max_chars: int = 200000) -> List[str]:
        paragraphs = [p.strip() for p in re.split(r"\n{2,}", text) if p.strip()]
        chunks: List[str] = []
        current = ""
        for paragraph in paragraphs:
            if len(paragraph) > max_chars:
                mid = len(paragraph) // 2
                chunks.extend(ExamGenerator._chunk_text(paragraph[:mid], max_chars))
                chunks.extend(ExamGenerator._chunk_text(paragraph[mid:], max_chars))
                continue
            if len(current) + len(paragraph) + 2 > max_chars and current:
                chunks.append(current)
                current = paragraph
            else:
                current = f"{current}\n\n{paragraph}" if current else paragraph
        if current:
            chunks.append(current)
        return chunks

    @staticmethod
    def _chunk_text_by_count(text: str, parts: int) -> List[str]:
        if parts <= 1:
            return [text]
        paragraphs = [p.strip() for p in re.split(r"\n{2,}", text) if p.strip()]
        if not paragraphs:
            return [text]
        total_len = sum(len(p) for p in paragraphs)
        target = max(1, total_len // parts)
        chunks: List[str] = []
        current = ""
        for paragraph in paragraphs:
            if len(current) + len(paragraph) + 2 > target and current:
                chunks.append(current)
                current = paragraph
            else:
                current = f"{current}\n\n{paragraph}" if current else paragraph
        if current:
            chunks.append(current)
        return chunks

    @staticmethod
    def evaluate_code(code: str, function_name: str, tests: List[dict]) -> dict:
        namespace = {}
        try:
            exec(code, namespace, namespace)
        except Exception as exc:
            return {"status": "error", "feedback": f"Code error: {exc}"}

        func = namespace.get(function_name)
        if not callable(func):
            return {"status": "error", "feedback": f"Function '{function_name}' not found."}

        for idx, test in enumerate(tests):
            try:
                inputs = test.get("input", [])
                if not isinstance(inputs, list):
                    inputs = [inputs]
                expected = test.get("output", None)
                result = func(*inputs)
                if result != expected:
                    return {
                        "status": "incorrect",
                        "feedback": f"Test {idx+1} failed. Expected {expected}, got {result}.",
                    }
            except Exception as exc:
                return {"status": "error", "feedback": f"Test {idx+1} error: {exc}"}
        return {"status": "correct", "feedback": "All tests passed."}
