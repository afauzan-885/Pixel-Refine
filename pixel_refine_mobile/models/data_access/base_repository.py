"""
pixel_refine_mobile/models/data_access/base_repository.py
---------------------------------------------------------
Base repository class for database operations.
Direct port from desktop — same API, same behavior.
"""

import sqlite3
from typing import Optional, Any, List, Union, Literal, overload
from contextlib import contextmanager


class BaseRepository:
    """
    Base class for all repositories.
    Provides database connection management and common operations.
    """

    def __init__(self, db_path: str):
        self.db_path = db_path

    @contextmanager
    def get_connection(self):
        """Context manager for database connections with WAL mode."""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path, timeout=30.0)
            conn.execute("PRAGMA journal_mode=WAL")
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
        """Context manager for database cursor with automatic commit."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                yield cursor
                if commit:
                    conn.commit()
            except Exception:
                conn.rollback()
                raise

    def execute_query(self, query: str, params: tuple = (), fetch_one: bool = False):
        """Execute a SELECT query and return results."""
        with self.get_cursor(commit=False) as cursor:
            cursor.execute(query, params)
            if fetch_one:
                return cursor.fetchone()
            return cursor.fetchall()

    def execute_update(self, query: str, params: tuple = ()) -> int:
        """Execute an INSERT, UPDATE, or DELETE query."""
        with self.get_cursor() as cursor:
            cursor.execute(query, params)
            return cursor.lastrowid if cursor.lastrowid else cursor.rowcount

    def execute_many(self, query: str, params_list: list) -> int:
        """Execute a query multiple times with different parameters."""
        with self.get_cursor() as cursor:
            cursor.executemany(query, params_list)
            return cursor.rowcount

    def table_exists(self, table_name: str) -> bool:
        """Check if a table exists in the database."""
        query = "SELECT name FROM sqlite_master WHERE type='table' AND name=?"
        result = self.execute_query(query, (table_name,), fetch_one=True)
        return result is not None

    def column_exists(self, table_name: str, column_name: str) -> bool:
        """Check if a column exists in a table."""
        query = f"PRAGMA table_info({table_name})"
        columns = self.execute_query(query, fetch_one=False)
        column_names = [col[1] for col in columns]
        return column_name in column_names

    def add_column_if_not_exists(self, table_name: str, column_name: str, column_def: str) -> bool:
        """Add a column to a table if it doesn't exist."""
        if not self.column_exists(table_name, column_name):
            query = f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_def}"
            self.execute_update(query)
            print(f"Added column '{column_name}' to table '{table_name}'")
            return True
        return False
