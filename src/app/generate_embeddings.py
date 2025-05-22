"""Module for the embeddings generation process."""

import re
from chromadb import PersistentClient
from chromadb.api.models.Collection import Collection
import ollama
import pymupdf
from .utils import Utils


class EmbeddingsGenerator:
    """Module for the embeddings generation process."""

    def __init__(self, book_filename: str):
        self.book_filename = book_filename
        self.output_folder = Utils.strip_extension(book_filename)
        self.chromaclient = PersistentClient(
            path=str(Utils.get_output_path(self.output_folder))
        )


    def get_toc(self, book: pymupdf.Document ) -> list:
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
    ) -> tuple[str, int, str, int]:
        """
        Retrieve an parses the PDF document by page, yielding text, level, title and page for each.
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
            toc = self.get_toc(book)
            page, toc_index = 0, 0
            while page < book.page_count and (toc_index + 1) < len(toc):
                text = book.load_page(page).get_text()
                segments = re.split(
                    r"\.\s*\n", text
                )  # Split texts by dot following by line break.
                segment_chunk = ""
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
                                )
                                start = (
                                    end - overlap
                                )  # overlap to counterweight truncated sentences
                        else:
                            if len(segment_chunk) + len(segment) < char_limit:
                                segment_chunk += ". \n"+segment
                            else:
                                data = (segment_chunk, toc[toc_index][0], toc[toc_index][1], page)
                                segment_chunk = segment
                                yield data

                if len(segment_chunk) > 0:
                    data = (segment_chunk, toc[toc_index][0], toc[toc_index][1], page)
                    yield data

                page += 1
                if page >= toc[(toc_index + 1)][2]:
                    toc_index += 1  # Advancing TOC headers (table of contents)

            Utils.logger.info(
                "The pdf parsing has finished, %s pages parsed.", book.page_count
            )

    def generate_embeddings(self) -> Collection:
        """
        Generates the embeedings using ollama, stores them in a collection.
        Returns:
        chromadb.api.models.Collection.Collection: The generated collection.
        """
        if Utils.COLLECTION_NAME in [
            collection.name for collection in self.chromaclient.list_collections()
        ]:
            Utils.logger.info(
                "Collection '%s' already exists. Deleting it and creating a new one.",
                Utils.COLLECTION_NAME,
            )
            self.chromaclient.delete_collection(Utils.COLLECTION_NAME)
        collection = self.chromaclient.create_collection(name="embeddings")
        batch_size = 1024
        batch = {"ids": [], "embeddings": [], "metadatas": [], "documents": []}
        idx = 0
        for text, level, title, page in self.parse_pdf():
            idx += 1
            response = ollama.embed(model=Utils.EMBEDDINGS_MODEL, input=text)
            Utils.logger.info(
                "Adding embeddings for level:   %s, page:  %s, title:   %s, textln:   %s",
                level,
                page,
                title,
                len(text),
            )
            batch["ids"].append(str(idx))
            batch["embeddings"].extend(response.get("embeddings", ""))
            batch["metadatas"].append({"level": level, "title": title, "page": page})
            batch["documents"].append(text)
            if len(batch["ids"]) == batch_size:
                Utils.logger.info("Saving a batch to chromadb....")
                collection.add(
                    ids=batch["ids"],
                    embeddings=batch["embeddings"],
                    metadatas=batch["metadatas"],
                    documents=batch["documents"]
                )
                batch = {"ids": [], "embeddings": [], "metadatas": [], "documents": []}
        return collection
