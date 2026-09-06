"""
Base repository class for database operations.
Provides common database connection and transaction management.
"""

import os
import sqlite3
from typing import Optional, overload, Any, List, Union, Literal
from contextlib import contextmanager


class BaseRepository:
    """
    Base class for all repositories.
    Provides database connection management and common operations.
    """

    def __init__(self, db_path: str):
        """
        Initialize repository with database path.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path

    @contextmanager
    def get_connection(self):
        """
        Context manager for database connections.
        Automatically handles connection cleanup and enables foreign keys.

        Yields:
            sqlite3.Connection: Database connection

        Example:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM images")
        """
        conn = None
        try:
            # Set timeout to 30.0 to help with concurrent access
            conn = sqlite3.connect(self.db_path, timeout=30.0)
            conn.execute(
                "PRAGMA journal_mode=WAL"
            )  # Write-Ahead Logging for concurrency
            conn.execute("PRAGMA foreign_keys = ON")
            yield conn
        except sqlite3.Error as e:
            if conn:
                conn.rollback()
            print(f"Database error in {self.__class__.__name__}: {e}")
            raise
        finally:
            if conn:
                conn.close()

    @contextmanager
    def get_cursor(self, commit: bool = True):
        """
        Context manager for database cursor with automatic commit.

        Args:
            commit: Whether to commit changes automatically (default: True)

        Yields:
            sqlite3.Cursor: Database cursor

        Example:
            with self.get_cursor() as cursor:
                cursor.execute("INSERT INTO images (path) VALUES (?)", (path,))
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                yield cursor
                if commit:
                    conn.commit()
            except Exception as e:
                conn.rollback()
                raise

    @overload
    def execute_query(
        self, query: str, params: tuple = (), fetch_one: Literal[True] = True
    ) -> Optional[tuple]: ...

    @overload
    def execute_query(
        self, query: str, params: tuple = (), fetch_one: Literal[False] = False
    ) -> List[tuple]: ...

    @overload
    def execute_query(
        self, query: str, params: tuple = (), fetch_one: bool = False
    ) -> Union[Optional[tuple], List[tuple]]: ...

    def execute_query(
        self, query: str, params: tuple = (), fetch_one: bool = False
    ) -> Any:
        """
        Execute a SELECT query and return results.

        Args:
            query: SQL query string
            params: Query parameters
            fetch_one: If True, return only first result

        Returns:
            Single row (if fetch_one=True) or list of rows
        """
        with self.get_cursor(commit=False) as cursor:
            cursor.execute(query, params)
            if fetch_one:
                return cursor.fetchone()
            return cursor.fetchall()

    def execute_update(self, query: str, params: tuple = ()) -> int:
        """
        Execute an INSERT, UPDATE, or DELETE query.

        Args:
            query: SQL query string
            params: Query parameters

        Returns:
            Number of affected rows or last inserted row ID
        """
        with self.get_cursor() as cursor:
            cursor.execute(query, params)
            # Return lastrowid for INSERT, rowcount for UPDATE/DELETE
            return cursor.lastrowid if cursor.lastrowid else cursor.rowcount

    def execute_many(self, query: str, params_list: list) -> int:
        """
        Execute a query multiple times with different parameters.

        Args:
            query: SQL query string
            params_list: List of parameter tuples

        Returns:
            Number of affected rows
        """
        with self.get_cursor() as cursor:
            cursor.executemany(query, params_list)
            return cursor.rowcount

    def table_exists(self, table_name: str) -> bool:
        """
        Check if a table exists in the database.

        Args:
            table_name: Name of the table

        Returns:
            True if table exists, False otherwise
        """
        query = "SELECT name FROM sqlite_master WHERE type='table' AND name=?"
        result = self.execute_query(query, (table_name,), fetch_one=True)
        return result is not None

    def column_exists(self, table_name: str, column_name: str) -> bool:
        """
        Check if a column exists in a table.

        Args:
            table_name: Name of the table
            column_name: Name of the column

        Returns:
            True if column exists, False otherwise
        """
        query = f"PRAGMA table_info({table_name})"
        columns = self.execute_query(query, fetch_one=False)
        column_names = [col[1] for col in columns]
        return column_name in column_names

    def add_column_if_not_exists(
        self, table_name: str, column_name: str, column_def: str
    ) -> bool:
        """
        Add a column to a table if it doesn't exist.

        Args:
            table_name: Name of the table
            column_name: Name of the column to add
            column_def: Column definition (e.g., "INTEGER NOT NULL DEFAULT 0")

        Returns:
            True if column was added, False if it already existed
        """
        if not self.column_exists(table_name, column_name):
            query = f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_def}"
            self.execute_update(query)
            if os.environ.get("PIXEL_REFINE_VERBOSE_LOGS", "0") == "1":
                print(
                    f"[Pixel Refine - Detail] Database column added: "
                    f"{table_name}.{column_name}"
                )
            return True
        return False
