"""
db_utils.py

Utility module for PostgreSQL database operations.

Features:
    - Establish PostgreSQL database connection.
    - Execute SELECT queries.
    - Execute INSERT, UPDATE and DELETE queries.
    - Automatic transaction handling.
    - Returns SELECT results as list of dictionaries.
    - Returns affected row count for write operations.
"""

import psycopg2
from psycopg2.extras import RealDictCursor

from .ace_logger import AceLogger


logger = AceLogger.get_logger("db_utils")


class DBUtils:
    """
    Utility class for PostgreSQL database operations.
    """

    @staticmethod
    def get_connection(host, port, database, username, password):
        """
        Create and return a PostgreSQL database connection.

        Args:
            host (str): Database host.
            port (int): Database port.
            database (str): Database name.
            username (str): Database username.
            password (str): Database password.

        Returns:
            psycopg2.extensions.connection:
                PostgreSQL connection object.

        Raises:
            psycopg2.Error:
                If connection fails.
        """

        try:

            logger.info(f"Connecting to database '{database}'.")

            connection = psycopg2.connect(
                host=host,
                port=port,
                database=database,
                user=username,
                password=password
            )

            logger.info("Database connection established successfully.")

            return connection

        except Exception as ex:

            logger.exception(f"Database connection failed: {ex}")

            raise

    @staticmethod
    def execute(connection, query, params=None):
        """
        Execute SQL query.

        Supports:
            - SELECT
            - INSERT
            - UPDATE
            - DELETE

        Args:
            connection:
                PostgreSQL connection object.

            query (str):
                SQL query.

            params (tuple, optional):
                Query parameters.

        Returns:
            list:
                SELECT query result as list of dictionaries.

            int:
                Number of affected rows for
                INSERT, UPDATE and DELETE.
        """

        cursor = connection.cursor(cursor_factory=RealDictCursor)

        try:

            logger.info("Executing SQL query.")

            cursor.execute(query, params)

            sql_type = query.strip().split()[0].upper()

            if sql_type == "SELECT":

                result = cursor.fetchall()

                logger.info(
                    f"Fetched {len(result)} record(s)."
                )

                return result

            connection.commit()

            affected_rows = cursor.rowcount

            logger.info(
                f"{affected_rows} row(s) affected."
            )

            return affected_rows

        except Exception as ex:

            connection.rollback()

            logger.exception(
                f"Query execution failed: {ex}"
            )

            raise

        finally:

            cursor.close()

    @staticmethod
    def close(connection):
        """
        Close PostgreSQL connection.

        Args:
            connection:
                Active PostgreSQL connection.
        """

        try:

            if connection:

                connection.close()

                logger.info("Database connection closed.")

        except Exception as ex:

            logger.exception(
                f"Failed to close database connection: {ex}"
            )