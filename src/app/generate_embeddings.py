"""Module for the embeddings generation process."""

import json
import re
import requests
from chromadb.api.models.Collection import Collection
import pymupdf
from .indexer import IndexBuilder
from .utils import Utils


class EmbeddingsGenerator:
    """Module for the embeddings generation process."""

    def __init__(self, book_filename: str):
        self.book_filename = book_filename
        self.book_page_length = "..."
        self.output_folder = Utils.strip_extension(book_filename)
        self.chromaclient = Utils.get_chroma_client(
            str(Utils.get_output_path(self.output_folder))
        )

    def get_toc(self, book: pymupdf.Document) -> list:
        """
        Retrieves the current book table of contens ignoring cover pages and retunrs it as a list of tuples.

        Args:
        book (pymupdf.Document): the opened document.
        Returns:
        list: A lis ot tuples with the TOC entries ignoring cover pages (negative numbered pages)
        """
        toc = []
        for level, title, page in book.get_toc():
            if page >= 0:
                toc.append((level, title, page))
        return toc

    def parse_pdf(
        self, char_limit: int = 2000, overlap: int = 200
    ) -> tuple[str, int, str, int, int, int]:
        """
        Retrieve an parses the PDF document by page, yielding text, level, title, page, and toc_index for each.
        The text of each page will be divided into segments, segments are blocks of text that ends with a dot
        and a line break, if a segment is too big (cahr_limit), for example bigger than 2k chars (rouglhy 500 tokens)
        it will be further divided in chunks no longer than char_limit with certain overlap.
        The function will try to clump small segments in a segment_chunk no longer than char_limit

        Args:
        char_limit (int): limit of character per chunk of text sent to the embedding model.
            default 2k assumin 4 chars = 1 token for the model 512 token limit
        overlap (int): how much character to overlap when splitting a text block into chunks, to retain consistence

        """
        Utils.logger.info("Retrieving /data/%s", self.book_filename)
        with pymupdf.open(f"{Utils.get_data_path()}/{self.book_filename}") as book:
            self.book_page_length = book.page_count
            toc = self.get_toc(book)
            page, toc_index = 0, 0
            while page < book.page_count and (toc_index + 1) < len(toc):
                page_obj = book.load_page(page)
                blocks = page_obj.get_text("blocks") or []
                raw_segments = []
                for block in sorted(blocks, key=lambda b: (b[1], b[0])):
                    block_text = block[4].strip()
                    if not block_text:
                        continue
                    raw_segments.extend(
                        [seg.strip() for seg in re.split(r"\n{2,}", block_text) if seg.strip()]
                    )
                segments = raw_segments
                segment_chunk = ""
                segment_index = 0
                for segment in segments:
                    if len(segment) > 0:  # Only work with valid segments
                        if (
                            len(segment) > char_limit
                        ):  # Split into chunks if segment bigger than char_limit
                            start = 0
                            while start < len(segment):
                                end = start + char_limit
                                chunk = segment[start:end]
                                yield (
                                    chunk,
                                    toc[toc_index][0],
                                    toc[toc_index][1],
                                    page,
                                    toc_index,
                                    segment_index,
                                )
                                segment_index += 1
                                start = (
                                    end - overlap
                                )  # overlap to counterweight truncated sentences
                        else:
                            if len(segment_chunk) + len(segment) < char_limit:
                                segment_chunk += ". \n" + segment
                            else:
                                data = (
                                    segment_chunk,
                                    toc[toc_index][0],
                                    toc[toc_index][1],
                                    page,
                                    toc_index,
                                    segment_index,
                                )
                                segment_chunk = segment
                                yield data
                                segment_index += 1

                if len(segment_chunk) > 0:
                    data = (
                        segment_chunk,
                        toc[toc_index][0],
                        toc[toc_index][1],
                        page,
                        toc_index,
                        segment_index,
                    )
                    yield data

                page += 1
                if page >= toc[(toc_index + 1)][2]:
                    toc_index += 1  # Advancing TOC headers (table of contents)

            Utils.logger.info(
                "The pdf parsing has finished, %s pages parsed.", book.page_count
            )

    def check_collection(self) -> bool:
        """Checks if the embeddings db for a book exist."""
        if Utils.COLLECTION_NAME in [
            collection.name for collection in self.chromaclient.list_collections()
        ]:
            return True
        return False

    def generate_embeddings(self, stream: bool = False, resume: bool = False) -> Collection:
        """
        Generates the embeedings using ollama, stores them in a collection.
        Returns:
        chromadb.api.models.Collection.Collection: The generated collection.
        """
        if not resume:
            self._clear_checkpoint()
        checkpoint = self._load_checkpoint() if resume else None
        if resume and not checkpoint:
            Utils.logger.warning(
                "Resume requested but no checkpoint found. Starting fresh."
            )
            resume = False
        resume_page = checkpoint.get("page", 0) if checkpoint else 0
        resume_segment = checkpoint.get("segment", -1) if checkpoint else -1
        idx = checkpoint.get("idx", 0) if checkpoint else 0

        if self.check_collection():
            if resume:
                collection = self.chromaclient.get_collection(name="embeddings")
            else:
                Utils.logger.info(
                    "Collection '%s' already exists. Deleting it and creating a new one.",
                    Utils.COLLECTION_NAME,
                )
                self.chromaclient.delete_collection(Utils.COLLECTION_NAME)
                collection = self.chromaclient.create_collection(name="embeddings")
        else:
            collection = self.chromaclient.create_collection(name="embeddings")
        batch_size = 1024
        batch = {
            "ids": [],
            "embeddings": [],
            "metadatas": [],
            "documents": [],
            "positions": [],
        }
        session = requests.Session()
        index_builder = IndexBuilder(self.book_filename)
        if resume:
            index_builder.load_json_index()
        for text, level, title, page, toc_index, segment_index in self.parse_pdf():
            if resume and (
                page < resume_page
                or (page == resume_page and segment_index <= resume_segment)
            ):
                continue
            if stream:
                yield f"data: {json.dumps({'progress': f'{page}/{self.book_page_length}'})}\n\n"
            idx += 1
            summary, topics = index_builder.summarize_segment(text)
            extra_context = ""
            if summary:
                extra_context += f"\n\nSummary: {summary}"
            if topics:
                extra_context += f"\nTopics: {', '.join(topics)}"
            embedding_text = text + extra_context
            response = session.post(
                Utils.OLLAMA_URL + "/embed",
                json={"model": Utils.EMBEDDINGS_MODEL, "input": embedding_text},
                timeout=180,
            )
            payload = response.json()
            embeddings = payload.get("embeddings", [])
            if not embeddings or not embeddings[0]:
                Utils.logger.warning(
                    "Skipping empty embedding for level: %s, page: %s, textln: %s",
                    level,
                    page,
                    len(text),
                )
                continue
            index_builder.add_segment(toc_index, text, summary=summary, topics=topics)
            Utils.logger.info(
                "Adding embeddings for level:   %s, page:  %s, textln:   %s",
                level,
                page,
                len(text),
            )
            batch["ids"].append(str(idx))
            batch["embeddings"].extend(embeddings)
            batch["metadatas"].append({"level": level, "title": title, "page": page})
            batch["documents"].append(text)
            batch["positions"].append(
                {"page": page, "segment": segment_index, "toc_index": toc_index}
            )
            if len(batch["ids"]) == batch_size:
                Utils.logger.info("Saving a batch to chromadb....")
                collection.add(
                    ids=batch["ids"],
                    embeddings=batch["embeddings"],
                    metadatas=batch["metadatas"],
                    documents=batch["documents"],
                )
                index_builder.write_json_index()
                index_builder.write_text_index()
                self._save_checkpoint(batch["positions"][-1], idx)
                batch = {
                    "ids": [],
                    "embeddings": [],
                    "metadatas": [],
                    "documents": [],
                    "positions": [],
                }
        # Save remaining embeddings that didnt filled a entire batch
        if batch["ids"]:
            Utils.logger.info("Saving remaining embeddings to chromadb....")
            collection.add(
                ids=batch["ids"],
                embeddings=batch["embeddings"],
                metadatas=batch["metadatas"],
                documents=batch["documents"],
            )
            index_builder.write_json_index()
            index_builder.write_text_index()
            self._save_checkpoint(batch["positions"][-1], idx)
        index_builder.write_json_index()
        index_builder.write_text_index()
        self._clear_checkpoint()
        if stream:
            yield f"data: {json.dumps({'progress': 'done'})}\n\n"
            return None
        return collection

    def _checkpoint_path(self):
        output_path = Utils.get_output_path(self.output_folder, create=True)
        return output_path / "embeddings_checkpoint.json"

    def _load_checkpoint(self) -> dict:
        checkpoint_path = self._checkpoint_path()
        if not checkpoint_path.exists():
            return {}
        try:
            with open(checkpoint_path, "r", encoding="utf-8") as handle:
                return json.load(handle)
        except Exception as exc:
            Utils.logger.warning("Failed to load checkpoint: %s", exc)
            return {}

    def _save_checkpoint(self, position: dict, idx: int) -> None:
        checkpoint_path = self._checkpoint_path()
        payload = {
            "page": position.get("page"),
            "segment": position.get("segment"),
            "toc_index": position.get("toc_index"),
            "idx": idx,
        }
        try:
            with open(checkpoint_path, "w", encoding="utf-8") as handle:
                json.dump(payload, handle, indent=2)
                handle.write("\n")
        except Exception as exc:
            Utils.logger.warning("Failed to save checkpoint: %s", exc)

    def _clear_checkpoint(self) -> None:
        checkpoint_path = self._checkpoint_path()
        try:
            if checkpoint_path.exists():
                checkpoint_path.unlink()
        except Exception as exc:
            Utils.logger.warning("Failed to clear checkpoint: %s", exc)

    def get_progress(self) -> dict:
        checkpoint = self._load_checkpoint()
        page_count = 0
        try:
            with pymupdf.open(f"{Utils.get_data_path()}/{self.book_filename}") as book:
                page_count = book.page_count
        except Exception as exc:
            Utils.logger.warning("Failed to read page count: %s", exc)

        has_checkpoint = bool(checkpoint)
        has_embeddings = self.check_collection()
        is_complete = has_embeddings and not has_checkpoint

        if has_checkpoint and "page" in checkpoint and page_count:
            parsed_pages = min(int(checkpoint["page"]) + 1, page_count)
        elif is_complete and page_count:
            parsed_pages = page_count
        else:
            parsed_pages = 0

        return {
            "page_count": page_count,
            "parsed_pages": parsed_pages,
            "has_checkpoint": has_checkpoint,
            "is_complete": is_complete,
        }
