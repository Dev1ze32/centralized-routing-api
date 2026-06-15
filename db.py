"""
Shared PostgreSQL connection helper.

Reads connection settings from environment variables (loaded from a
.env file via python-dotenv). Copy .env.example to .env and fill in
your own credentials.
"""

import os

import psycopg2
import psycopg2.extras
from dotenv import load_dotenv

load_dotenv()


def get_connection():
    """Return a new psycopg2 connection using settings from .env"""
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("DB_NAME", "routing_db"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", "postgres"),
    )


def get_dict_cursor(conn):
    """Return a cursor that returns rows as dict-like objects."""
    return conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)