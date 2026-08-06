import pyodbc


class DBUtils:
    """
    Utility class for establishing SQL Server database connections.

    This class provides reusable methods for creating database connections
    using the Microsoft ODBC Driver for SQL Server. It is intended to be
    shared across multiple services or applications.

    Features:
        - Creates SQL Server connections using pyodbc.
        - Supports dynamic database configuration.
        - Returns an active database connection object.

    Supported Database:
        - Microsoft SQL Server

    Example:
        >>> conn = DBUtils.get_connection(
        ...     host="localhost",
        ...     port=1433,
        ...     database="user_auth",
        ...     username="sa",
        ...     password="password"
        ... )
    """

    @staticmethod
    def get_connection(host, port, database, username, password):
        """
        Establish a connection to a SQL Server database.

        Builds an ODBC connection string using the supplied database
        credentials and returns an active pyodbc connection object.

        Args:
            host (str): SQL Server hostname or IP address.
            port (int | str): SQL Server port number.
            database (str): Name of the database to connect to.
            username (str): SQL Server login username.
            password (str): SQL Server login password.

        Returns:
            pyodbc.Connection:
                An active database connection object.

        Raises:
            pyodbc.Error:
                If the connection to the database cannot be established.
        """
        connection_string = (
            f"DRIVER={{ODBC Driver 18 for SQL Server}};"
            f"SERVER={host},{port};"
            f"DATABASE={database};"
            f"UID={username};"
            f"PWD={password};"
            "TrustServerCertificate=yes;"
        )

        return pyodbc.connect(connection_string)