"""SQL Client for executing raw SQL queries using SQLAlchemy engine."""
from src.app.core.log_config import setup_logging
from contextlib import contextmanager
from src.app.core.database import engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text

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
                logger.error(f"[Session] An error occurred during session: {e}")
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
                logger.error(f"[Execute without params] Error executing query: {e}")
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
                logger.error(f"[Execute with params] Error executing query: {e}")
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
                    logger.info(f"[Insert] (Batch) Inserted multiple records.")
                    return {"status": "success"}
                else:
                    connection.execute(text(query), values or {})
                    logger.info(f"[Insert] Inserted single record.")
                    return {"status": "success"}

        except SQLAlchemyError as e:
            logger.error(f"[Insert] Error executing insert: {e}")
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
                logger.info(f"[Insert Returning ID] Inserted record with ID: {inserted_id}")
                return inserted_id
        except SQLAlchemyError as e:
            logger.error(f"[Insert Returning ID] Error executing insert: {e}")
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
                    logger.info(f"[Fetch All] Retrieved {len(rows)} records.")
                    return rows
                else:
                    rows = result.fetchall()
                    logger.info(f"[Fetch All] Retrieved {len(rows)} records.")
                    return rows
        except SQLAlchemyError as e:
            logger.error(f"[Fetch All] Error executing fetch: {e}")
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
                    if as_dict:
                        record = dict(row)
                    else:
                        record = row
                    logger.info(f"[Fetch One] Retrieved record")
                    return record
                else:
                    logger.info("[Fetch One] No record found.")
                    return None
        except SQLAlchemyError as e:
            logger.error(f"[Fetch One] Error executing fetch: {e}")
            raise