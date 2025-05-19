"""Module for the embeddings generation process."""

import chromadb
import ollama
import pymupdf
from .utils import Utils
# import sys

class EmbeddingsGenerator:
    """Module for the embeddings generation process."""

    def __init__(self, book_filename: str = ""):
        self.book_filename = book_filename
        self.outputfolder = Utils.strip_extension(book_filename)
        self.chromaclient = chromadb.PersistentClient(
            path = str(Utils.get_output_path(self.outputfolder))
        )

    def parse_pdf(self) -> None:
        """
        Retrieve an parses the PDF document by page, yielding text, level, title and page for each
        """
        Utils.logger.info("Retrieving /data/%s", self.book_filename)
        data_path = Utils.get_data_path()
        with pymupdf.open(f"{data_path}/{self.book_filename}") as book:
            # print(book.get_toc())
            # sys.exit(0)
            for level, title, page in book.get_toc():
                data = (book.load_page(page).get_text(), level, title, page)
                yield data
            Utils.logger.info(
                "The pdf parsing has finished, %s pages parsed.", book.page_count
            )

    def generate_embeddings(self) -> bool:
        """
        Generates the embeedings using ollama, stores them in a collection.
        Returns:
        bool: True if finished. Will throw exception otherwise.
        """
        collection_name = "embeddings"
        if collection_name in [collection.name for collection in self.chromaclient.list_collections()]:
            Utils.logger.info("Collection '%s' already exists. Deleting it and creating a new one.", collection_name)
            self.chromaclient.delete_collection(collection_name)
        collection = self.chromaclient.create_collection(name="embeddings")
        limit = 10
        for text, level, title, page in self.parse_pdf():
            limit -= 1
            if limit <= 0:
                break
            response = ollama.embed(model="mxbai-embed-large", input=text)
            Utils.logger.info(
                "Adding embeddings for level: %s, title: %s, page: %s, text len: %s",
                level,
                title,
                page,
                len(text)
            )

            collection.add(
                ids=[str(page)],
                embeddings=response["embeddings"],
                metadatas=[{"level": level, "title": title, "page": page}]
            )
        return True
