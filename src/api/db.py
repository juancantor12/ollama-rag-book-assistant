"""Data layer for the api users."""

from typing import List
from sqlalchemy import create_engine, event, inspect, MetaData
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import SQLAlchemyError
from app.utils import Utils


Base = declarative_base()


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, _connection_record):
    """Listener to enable foreign keys on sqlite connections."""
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


class Database:
    """Data layer for the API using SQLAlchemy."""

    def __init__(self, db_url: str = f"sqlite:///{str(Utils.get_api_db_path())}"):
        """
        Initializes the database connection.
        Args:
        db_url (str): URL for the SQLite database.
        """
        Utils.logger.info("Initializing database at %s", db_url)
        self.engine = create_engine(db_url)
        self.metadata = MetaData()
        self.session_maker = sessionmaker(bind=self.engine)
        self.session = self.session_maker()

    def create_all_tables(self) -> bool:
        """Create all tables defined in the models."""
        try:
            Utils.logger.info("Creating tables...")
            Base.metadata.create_all(self.engine)
            return True
        except SQLAlchemyError as e:
            Utils.logger.error("Error creating tables: %s", str(e))
            return False

    def list_tables(self) -> List[str]:
        """Lists all table names in the database."""
        try:
            inspection = inspect(self.engine)
            return inspection.get_table_names()
        except SQLAlchemyError as e:
            Utils.logger.error("Error listing tables: %s", str(e))
            return []

    def table_exists(self, table_name: str) -> bool:
        """Checks if a table exists in the database."""
        return table_name in self.list_tables()
