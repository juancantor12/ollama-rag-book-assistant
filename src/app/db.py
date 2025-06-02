"""Data layer for the api users. This module is UNUSED for now but will repace ChromaDB access in other modules"""

from typing import List, Union
from chromadb import PersistentClient
from chromadb.api.models.Collection import Collection
from app.utils import Utils


class Database:
    """Data layer for the api users."""

    def __init__(self):
        Utils.logger.info("Initializing users db at data/")
        self.chromaclient = PersistentClient(path=str(Utils.get_data_path()))

    def create_collection(
        self, collection_name: str, overwrite: bool = False
    ) -> Union[None, Collection]:
        """
        Creates a collection if it doesnt exists, if 'overwrite' is True, deletes the
        existing collections and creates an empty, new one.
        Args:
        collection_name (str): Name of the collection to create
        overwrite (bool): If an existing collection should be overwritten, defaults to False
        Returns:
        Union[None, Collection]: The created collection, None if the creation failed
        """

        if collection_name in self.list_collections():
            Utils.logger.warning("Collection '%s' already exists.", collection_name)
            if overwrite:
                Utils.logger.warning("Overriding existing collection.")
                self.delete_collection(collection_name)
                Utils.logger.info("Creating collection '%s'...", collection_name)
                return self.chromaclient.create_collection(name=collection_name)
            Utils.logger.error(
                "Unable to create collection '%s'. Already exists.", collection_name
            )
            return None
        Utils.logger.info("Creating collection '%s'...", collection_name)
        return self.chromaclient.create_collection(name=collection_name)

    def get_collection(self, collection_name: str) -> Union[None, Collection]:
        """
        Retrieves a collection if it exists.
        Args:
        collection_name (str): Name of the collection to retrieve
        Returns:
        Union[None, Collection]: The collection, or None if it wasnt found.
        """
        if collection_name in self.list_collections():
            return self.chromaclient.get_collection(name=collection_name)
        Utils.logger.error("Unable to get collection '%s'. Not found.", collection_name)
        return None

    def list_collections(self) -> List[str]:
        """Retrieves a list of the current database collections."""
        return [c.name for c in self.chromaclient.list_collections()]

    def delete_collection(self, collection_name: str) -> None:
        """
        Deletes a collection if it exists.
        Args:
        collection_name (str): Name of the collection to delete
        """
        if collection_name in self.list_collections():
            Utils.logger.warning("Deleting collection '%s'", collection_name)
            self.chromaclient.delete_collection(collection_name)
        Utils.logger.error(
            "Unable to delete collection '%s'. Not found.", collection_name
        )
