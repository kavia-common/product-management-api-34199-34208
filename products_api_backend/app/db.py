import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path

from flask import current_app

# PUBLIC_INTERFACE
def get_database_path() -> str:
    """Return the filesystem path to the SQLite database.

    Uses the environment variable DB_PATH if set; otherwise defaults to
    an app instance path database file 'products.db'.
    """
    db_env_path = os.getenv("DB_PATH", "").strip()
    if db_env_path:
        return db_env_path

    # Default to instance folder/products.db to allow writable location
    instance_path = getattr(current_app, "instance_path", None)
    if not instance_path:
        # Fallback to local directory if current_app not set (e.g., CLI initialization)
        instance_path = os.path.join(os.getcwd(), "instance")
    Path(instance_path).mkdir(parents=True, exist_ok=True)
    return os.path.join(instance_path, "products.db")


@contextmanager
def get_connection():
    """Context manager that yields a SQLite connection with row factory as dict-like."""
    db_path = get_database_path()
    conn = sqlite3.connect(db_path)
    # Return rows as dictionaries
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


# PUBLIC_INTERFACE
def init_db():
    """Initialize the SQLite database with the products table if it does not exist."""
    schema_sql = """
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        price REAL NOT NULL CHECK (price >= 0),
        quantity INTEGER NOT NULL CHECK (quantity >= 0)
    );
    """
    with get_connection() as conn:
        conn.execute(schema_sql)
