"""SQL Client for executing raw SQL queries using SQLAlchemy engine."""
from contextlib import contextmanager
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from src.app.core.log_config import setup_logging
from src.app.core.database import engine

logger = setup_logging("SQL Client")

class SQLClient:
    """
    SQL Client for executing raw SQL queries using SQLAlchemy engine.
    """
    def __init__(self):
        self.engine = engine

    @contextmanager
    def session(self):
        """
        Context manager to get a database connection.
        Sets up a transactional DB connection.
        """
        with self.engine.begin() as connection:
            try:
                yield connection
            except SQLAlchemyError as e:
                logger.error("[Session] An error occurred during session: %s", e)
                raise
            finally:
                logger.info("[Session] Closing database connection.")

    def execute_without_params(self, query: str):
        """
        Execute a raw SQL query without parameters within a managed session.

        :param query: The SQL query to execute.
        :return: ResultProxy containing the results of the query.
        """
        with self.session() as connection:
            try:
                result = connection.execute(text(query))
                return result
            except SQLAlchemyError as e:
                logger.error("[Execute without params] Error executing query: %s", e)
                raise

    def execute_with_params(self, query: str, params: dict = None):
        """
        Execute a raw SQL query with parameters within a managed session.

        :param query: The SQL query to execute.
        :param params: Optional parameters for the SQL query.
        :return: ResultProxy containing the results of the query.
        """
        with self.session() as connection:
            try:
                result = connection.execute(text(query), params or {})
                return result
            except SQLAlchemyError as e:
                logger.error("[Execute with params] Error executing query: %s", e)
                raise

    def insert(self, query: str, values: dict | list[dict] = None):
        """
        Executes an INSERT query with the provided values, and returns None.
        
        :param query: query to be executed
        :param values: values to be inserted
        """
        try:
            with self.session() as connection:
                if isinstance(values, list) and isinstance(values[0], dict):
                    connection.execute(text(query), values)
                    logger.info("[Insert] (Batch) Inserted multiple records.")
                    return {"status": "success"}
                connection.execute(text(query), values or {})
                logger.info("[Insert] Inserted single record.")
                return {"status": "success"}

        except SQLAlchemyError as e:
            logger.error("[Insert] Error executing insert: %s", e)
            raise

    def insert_returning_id(self, query: str, values: dict = None) -> int:
        """
        Executes an INSERT query with the provided values, and returns the inserted record's ID.
        
        :param query: query to be executed
        :param values: values to be inserted
        :return: ID of the inserted record
        """
        try:
            with self.session() as connection:
                result = connection.execute(text(query), values or {})
                inserted_id = result.scalar_one_or_none()
                logger.info("[Insert Returning ID] Inserted record with ID: %s", inserted_id)
                return inserted_id
        except SQLAlchemyError as e:
            logger.error("[Insert Returning ID] Error executing insert: %s", e)
            raise

    def fetch_all(self, query: str, params: dict = None, as_dict: bool = True):
        """
        Execute a SELECT query and return all results as a list of dictionaries.

        :param query: The SQL query to execute.
        :param params: Optional parameters for the SQL query.
        :return: List of dictionaries representing the result set.
        """
        try:
            with self.session() as connection:
                result = connection.execute(text(query), params or {})
                if as_dict:
                    results = result.fetchall()
                    rows = [{row[0] : row[1]} for row in results]
                    logger.info("[Fetch All] Retrieved %d records.", len(rows))
                    return rows
                rows = result.fetchall()
                logger.info("[Fetch All] Retrieved %d records.", len(rows))
                return rows
        except SQLAlchemyError as e:
            logger.error("[Fetch All] Error executing fetch: %s", e)
            raise

    def fetch_one(self, query: str, params: dict = None, as_dict: bool = True) -> dict | None:
        """
        Execute a SELECT query and return a single result as a dictionary.

        :param query: The SQL query to execute.
        :param params: Optional parameters for the SQL query.
        :return: A dictionary representing the single result, or None if no result.
        """
        try:
            with self.session() as connection:
                result = connection.execute(text(query), params or {})
                row = result.mappings().first() if as_dict else result.first()
                if row:
                    if not as_dict:
                        record = row
                    record = dict(row)
                    return record
                logger.info("[Fetch One] No record found.")
                return None
        except SQLAlchemyError as e:
            logger.error("[Fetch One] Error executing fetch: %s", e)
            raise
