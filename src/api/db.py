"""Data layer for the api users."""

from typing import List, Union
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import SQLAlchemyError
from app.utils import Utils
from sqlalchemy.ext.declarative import as_declarative
from sqlalchemy.orm import Query


# Create a Base class for declarative models
Base = declarative_base()

class Database:
    """Data layer for the API using SQLAlchemy."""
    
    def __init__(self, db_url: str = "sqlite:///data/users.db"):
        """
        Initializes the database connection.
        Args:
        db_url (str): URL for the SQLite database (default is sqlite:///data/users.db).
        """
        Utils.logger.info(f"Initializing database at {db_url}")
        self.engine = create_engine(db_url)
        self.metadata = MetaData()
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()

        # Create tables if they don't exist yet
        self._create_all_tables()

    def _create_all_tables(self):
        """Create all tables defined in the models."""
        try:
            Utils.logger.info("Creating tables...")
            Base.metadata.create_all(self.engine)
        except SQLAlchemyError as e:
            Utils.logger.error(f"Error creating tables: {str(e)}")

    def create_table(self, table_name: str, model_class: Base) -> Union[None, Table]:
        """
        Creates a table based on a model class (e.g., User).
        Args:
        table_name (str): Name of the table to create.
        model_class (Base): SQLAlchemy model class (e.g., User).
        Returns:
        Union[None, Table]: The created table, None if the creation failed.
        """
        try:
            if self.table_exists(table_name):
                Utils.logger.warning(f"Table '{table_name}' already exists.")
                return None  # You can choose to skip or override the table here
            else:
                model_class.__table__.create(self.engine)  # Create the table based on the model
                Utils.logger.info(f"Created table '{table_name}'.")
                return model_class.__table__
        except SQLAlchemyError as e:
            Utils.logger.error(f"Error creating table '{table_name}': {str(e)}")
            return None

    def query_table(self, table_name: str, model_class: Base, filters: dict = None) -> List[dict]:
        """
        Queries a table based on the model class (e.g., User).
        Args:
        table_name (str): Name of the table to query.
        model_class (Base): SQLAlchemy model class (e.g., User).
        filters (dict): Optional dictionary of filters for querying the table.
        Returns:
        List[dict]: A list of records matching the query.
        """
        try:
            query = self.session.query(model_class)
            if filters:
                for column, value in filters.items():
                    query = query.filter(getattr(model_class, column) == value)
            result = query.all()
            return [record.as_dict() for record in result]  # Assuming your model has `as_dict` method
        except SQLAlchemyError as e:
            Utils.logger.error(f"Error querying table '{table_name}': {str(e)}")
            return []

    def list_tables(self) -> List[str]:
        """Lists all table names in the database."""
        try:
            tables = self.engine.table_names()
            return tables
        except SQLAlchemyError as e:
            Utils.logger.error(f"Error listing tables: {str(e)}")
            return []

    def delete_table(self, table_name: str, model_class: Base) -> bool:
        """
        Deletes a table by its name.
        Args:
        table_name (str): Name of the table to delete.
        model_class (Base): SQLAlchemy model class (e.g., User).
        Returns:
        bool: True if the table was deleted, False if not.
        """
        try:
            if not self.table_exists(table_name):
                Utils.logger.error(f"Table '{table_name}' does not exist.")
                return False
            else:
                model_class.__table__.drop(self.engine)  # Drop the table
                Utils.logger.info(f"Deleted table '{table_name}'.")
                return True
        except SQLAlchemyError as e:
            Utils.logger.error(f"Error deleting table '{table_name}': {str(e)}")
            return False

    def table_exists(self, table_name: str) -> bool:
        """
        Checks if a table exists in the database.
        Args:
        table_name (str): Name of the table to check.
        Returns:
        bool: True if the table exists, False if not.
        """
        return table_name in self.list_tables()
