
import sqlite3
from app.config import get_settings


def get_connection():
    connection = sqlite3.connect("usage.db", timeout=5)
    connection.row_factory = sqlite3.Row
    return connection


def check_database() -> bool:
    try:
        with get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT 1")
            return cursor.fetchone()[0] == 1
    except Exception:
        return False


def initialize_usage_table() -> None:
    with get_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS llm_usage (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                model TEXT NOT NULL,
                input_tokens INTEGER NOT NULL,
                output_tokens INTEGER NOT NULL,
                estimated_cost_usd REAL NOT NULL,
                fallback_used INTEGER NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)


def record_usage(result: dict) -> None:
    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO llm_usage (
                model, input_tokens, output_tokens,
                estimated_cost_usd, fallback_used
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                result["model"],
                result["input_tokens"],
                result["output_tokens"],
                result["estimated_cost_usd"],
                int(result["fallback_used"]),
            ),
        )


def get_usage_totals() -> dict:
    with get_connection() as connection:
        row = connection.execute("""
            SELECT
                COUNT(*) AS requests,
                COALESCE(SUM(input_tokens), 0) AS input_tokens,
                COALESCE(SUM(output_tokens), 0) AS output_tokens,
                COALESCE(SUM(estimated_cost_usd), 0)
                    AS estimated_cost_usd,
                COALESCE(SUM(fallback_used), 0)
                    AS fallback_requests
            FROM llm_usage
        """).fetchone()

        return dict(row)
