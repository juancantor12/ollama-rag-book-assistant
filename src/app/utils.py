"""Shared utilities for the app."""

import os
from pathlib import Path
from typing import Union
from chromadb import PersistentClient
from chromadb.api.models.Collection import Collection
from app.logging import setup_logging

class Utils:
    """Utilities for the CV builder."""

    logger = setup_logging("default")
    # Sensitive
    API_SECRET_KEY = os.getenv("API_SECRET_KEY")
    API_TOKEN_ALGORITHM = os.getenv("API_TOKEN_ALGORITHM")
    API_TOKEN_EXPIRE_MINUTES = int(os.getenv("API_TOKEN_EXPIRE_MINUTES", "10"))
    API_DB_NAME = os.getenv("API_DB_NAME", "users.db")

    # Environment-specific
    COLLECTION_NAME = os.getenv("COLLECTION_NAME", "embeddings")
    DEFAULT_DB_FILENAME = os.getenv("DEFAULT_DB_FILENAME", "chroma.sqlite3")
    CHAT_MODEL = os.getenv("CHAT_MODEL")
    EMBEDDINGS_MODEL = os.getenv("EMBEDDINGS_MODEL")
    N_DOCUMENTS = int(os.getenv("N_DOCUMENTS", "3"))

    def __init__(self, output_folder_name):
        self.output_folder_name = output_folder_name

    @staticmethod
    def get_output_path(output_folder_name: str, create: bool = False) -> Path:
        """
        Returns the absolute output path for a given folder name.

        Args:
        output_folder_name (str): The name of the folder inside /output/ whose absolute path is requiered
        create (bool, optional): Whether to create the directory if it doesn't exist. Defaults to False.

        Returns:
        str: The absolute path to the required output folder.
        """
        path = f"output/{output_folder_name}"
        root_path = Path(__file__).resolve().parents[2]
        output_path = root_path / path
        if create:
            Path(output_path).mkdir(exist_ok=True)
        return output_path

    @staticmethod
    def get_data_path() -> Path:
        """
        Returns the absolute data path.

        Returns:
        str: the absolute path to the /data/ folder of the app
        """
        path = "data"
        root_path = Path(__file__).resolve().parents[2]
        data_path = root_path / path
        return data_path

    @staticmethod
    def save_file_to_output(
        output_folder_name: str, file_name: str, content: str, create: bool = True
    ) -> bool:
        """
        Saves a text file to a subfolder in /output, if the folder doesnt exists it is created

        Args:
        output_folder_name (str): The name of the folder inside /output/ where the file should be stored
        file_name (str): The name with which the file will be saved
        content (str): The tex content of the file to be saved
        create (bool, optional): Whether to create the directory if it doesn't exist. Defaults to False.

        Returns:
        bool: Wether the file was saved successfully, if the save fails file.write will raise an exception.
        """
        output_path = Utils.get_output_path(output_folder_name, create=create)
        with open(f"{output_path}/{file_name}", "w", encoding="utf-8") as file:
            file.write(content)
            print(f"Saving to output/{file_name}")

        return True

    @staticmethod
    def strip_extension(file_name: str) -> str:
        """
        Strips the extension of the name of a file and returns the filename without the extension

        Args:
        file_name (str): the name of the file with extension, may have several dots

        Returns:
        str: the file name stripped of the extension
        """
        if "." in file_name:
            segments = file_name.split(".")
            return ".".join(segments[:-1])
        return file_name

    @staticmethod
    def get_embeddings_db(output_folder: str) -> Union[None, Collection]:
        """
        Checks if a chromadb embeddings vector database exists within the specifief output folder
        If the database exists, the function checks from the embeddings collection and lastly, the
        collection exists, the function checks for the amount of records, if there are no records or
        either the collection or the database doesn't exist it returns None, otherwise returns the collection.

        Args:
        output_folder (str): The output folder where the database file should be

        Returns:
        Union[None, chromadb.api.models.Collection.Collection]: the collection
        """
        output_path = Utils.get_output_path(output_folder)
        if (Path(output_path) / Utils.DEFAULT_DB_FILENAME).exists():
            client = PersistentClient(path=str(output_path))
            if Utils.COLLECTION_NAME in [c.name for c in client.list_collections()]:
                collection = client.get_collection(name=Utils.COLLECTION_NAME)
                if collection.count() > 0:
                    return collection
                return None
            return None
        return None

    @staticmethod
    def get_api_db_path() -> Path:
        """Returns the api DB path."""
        return Utils.get_data_path() / Utils.API_DB_NAME
