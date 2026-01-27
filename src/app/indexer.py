"""Index builder for chapter/topic summaries."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple

import pymupdf
import requests

from .utils import Utils


@dataclass
class IndexNode:
    """Represents a chapter/subchapter entry in the index."""

    index: int
    level: int
    number: str
    title: str
    page_start: int
    page_end: int
    summary_lines: List[str] = field(default_factory=list)
    topics: Set[str] = field(default_factory=set)
    children: List["IndexNode"] = field(default_factory=list)

    def add_summary(self, summary: str, max_lines: int = 4) -> None:
        cleaned = summary.strip()
        if not cleaned:
            return
        if len(cleaned) > 220:
            cleaned = cleaned[:220].rstrip() + "..."
        existing = {line.lower() for line in self.summary_lines}
        if cleaned.lower() not in existing and len(self.summary_lines) < max_lines:
            self.summary_lines.append(cleaned)

    def add_topics(self, topics: List[str], max_topics: int = 30) -> None:
        for topic in topics:
            cleaned = re.sub(r"\s+", " ", topic.strip())
            cleaned = re.sub(r"[^A-Za-z0-9 _-]", "", cleaned)
            if cleaned:
                self.topics.add(cleaned.lower())
            if len(self.topics) >= max_topics:
                break


class IndexBuilder:
    """Builds a chapter/topic index while parsing the PDF."""

    def __init__(self, book_filename: str):
        self.book_filename = book_filename
        self.output_folder = Utils.strip_extension(book_filename)
        self.nodes: List[IndexNode] = []
        self.root_nodes: List[IndexNode] = []
        self._build_nodes_from_toc()

    def _build_nodes_from_toc(self) -> None:
        with pymupdf.open(f"{Utils.get_data_path()}/{self.book_filename}") as book:
            page_count = book.page_count
            toc = [
                (lvl, title, page) for lvl, title, page in book.get_toc() if page >= 0
            ]
        if not toc:
            return
        max_level = max(entry[0] for entry in toc)
        counts = [0] * (max_level + 1)
        nodes: List[IndexNode] = []
        for idx, (level, title, page_start) in enumerate(toc):
            page_end = page_count - 1
            for j in range(idx + 1, len(toc)):
                next_level, _next_title, next_page = toc[j]
                if next_level <= level:
                    page_end = max(next_page - 1, page_start)
                    break
            counts[level] += 1
            for i in range(level + 1, len(counts)):
                counts[i] = 0
            number = ".".join(
                str(counts[i]) for i in range(1, level + 1) if counts[i] > 0
            )
            nodes.append(
                IndexNode(
                    index=idx,
                    level=level,
                    number=number,
                    title=title,
                    page_start=page_start,
                    page_end=page_end,
                )
            )

        stack: List[IndexNode] = []
        roots: List[IndexNode] = []
        for node in nodes:
            while stack and stack[-1].level >= node.level:
                stack.pop()
            if stack:
                stack[-1].children.append(node)
            else:
                roots.append(node)
            stack.append(node)

        self.nodes = nodes
        self.root_nodes = roots

    def add_segment(
        self,
        toc_index: int,
        segment_text: str,
        summary: Optional[str] = None,
        topics: Optional[List[str]] = None,
    ) -> None:
        if toc_index < 0 or toc_index >= len(self.nodes):
            return
        if summary is None or topics is None:
            summary, topics = self._summarize_segment(segment_text)
        node = self.nodes[toc_index]
        node.add_summary(summary)
        node.add_topics(topics)

    def summarize_segment(self, segment_text: str) -> Tuple[str, List[str]]:
        """Expose summarization for embedding hints."""
        return self._summarize_segment(segment_text)

    def write_text_index(self, file_name: str = "topics_index.txt") -> None:
        output_path = Utils.get_output_path(self.output_folder, create=True)
        file_path = output_path / file_name
        lines = [
            f"Book: {self.book_filename}",
            "Index:",
        ]
        for node in self.root_nodes:
            self._render_node(node, lines, indent=0)
        safe_lines = [
            line.encode("utf-8", "replace").decode("utf-8") for line in lines
        ]
        with open(file_path, "w", encoding="utf-8") as handle:
            handle.write("\n".join(safe_lines).rstrip() + "\n")

    def write_json_index(self, file_name: str = "topics_index.json") -> None:
        output_path = Utils.get_output_path(self.output_folder, create=True)
        file_path = output_path / file_name
        payload = {
            "book_filename": self.book_filename,
            "entries": [self._node_to_dict(node) for node in self.root_nodes],
        }
        with open(file_path, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, ensure_ascii=True)
            handle.write("\n")

    def load_json_index(self, file_name: str = "topics_index.json") -> bool:
        output_path = Utils.get_output_path(self.output_folder, create=True)
        file_path = output_path / file_name
        if not file_path.exists():
            return False
        try:
            with open(file_path, "r", encoding="utf-8") as handle:
                payload = json.load(handle)
        except Exception as exc:
            Utils.logger.warning("Failed to load index json: %s", exc)
            return False
        entries = payload.get("entries", [])
        if not isinstance(entries, list):
            return False

        flattened: Dict[Tuple[str, str, int, int, int], Dict[str, object]] = {}
        stack = list(entries)
        while stack:
            entry = stack.pop()
            if not isinstance(entry, dict):
                continue
            key = (
                str(entry.get("number", "")),
                str(entry.get("title", "")),
                int(entry.get("page_start", 0)),
                int(entry.get("page_end", 0)),
                int(entry.get("level", 0)),
            )
            flattened[key] = entry
            children = entry.get("children", [])
            if isinstance(children, list):
                stack.extend(children)

        for node in self.nodes:
            key = (node.number, node.title, node.page_start, node.page_end, node.level)
            entry = flattened.get(key)
            if not entry:
                continue
            summary_lines = entry.get("summary_lines")
            if isinstance(summary_lines, list):
                node.summary_lines = [str(line) for line in summary_lines if str(line)]
            else:
                summary = str(entry.get("summary", "")).strip()
                node.summary_lines = [summary] if summary else []
            topics = entry.get("topics", [])
            if isinstance(topics, list):
                node.topics = {str(topic) for topic in topics if str(topic)}
        return True

    def _render_node(self, node: IndexNode, lines: List[str], indent: int) -> None:
        pad = " " * indent
        lines.append(
            f"{pad}{node.number} {node.title} (pages {node.page_start}-{node.page_end})"
        )
        if node.summary_lines:
            summary = " ".join(node.summary_lines)
            lines.append(f"{pad}  Summary: {summary}")
        if node.topics:
            topics = ", ".join(sorted(node.topics))
            lines.append(f"{pad}  Topics: {topics}")
        for child in node.children:
            self._render_node(child, lines, indent=indent + 2)

    def _node_to_dict(self, node: IndexNode) -> Dict[str, object]:
        return {
            "number": node.number,
            "title": node.title,
            "level": node.level,
            "page_start": node.page_start,
            "page_end": node.page_end,
            "summary": " ".join(node.summary_lines).strip(),
            "summary_lines": list(node.summary_lines),
            "topics": sorted(node.topics),
            "children": [self._node_to_dict(child) for child in node.children],
        }

    def _summarize_segment(self, segment_text: str) -> Tuple[str, List[str]]:
        if not Utils.CHAT_MODEL:
            return "", []
        prompt = (
            "Summarize the segment in 1 short sentence and list 3-8 topic keywords.\n"
            "Return only JSON with keys: summary (string), topics (array of strings).\n"
            "Segment:\n"
            f"{segment_text}"
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
                timeout=120,
            )
            raw = response.json().get("response", "").strip()
            data = self._safe_json(raw)
            if not data:
                return "", []
            summary = str(data.get("summary", "")).strip()
            topics = data.get("topics", [])
            if not isinstance(topics, list):
                topics = []
            topics = [str(topic) for topic in topics if str(topic).strip()]
            return summary, topics
        except Exception as exc:
            Utils.logger.warning("Index segment summarization failed: %s", exc)
            return "", []

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
