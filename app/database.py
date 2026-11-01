import os

import psycopg
from psycopg.rows import dict_row


def get_connection():
    database_url = os.getenv("DATABASE_URL", "")

    if not database_url:
        raise RuntimeError("DATABASE_URL is not configured")

    return psycopg.connect(database_url, connect_timeout=5)


def check_database() -> bool:
    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                return cursor.fetchone() == (1,)
    except Exception:
        return False


def initialize_usage_table() -> None:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS llm_usage (
                    id BIGSERIAL PRIMARY KEY,
                    model VARCHAR(100) NOT NULL,
                    input_tokens INTEGER NOT NULL,
                    output_tokens INTEGER NOT NULL,
                    estimated_cost_usd DOUBLE PRECISION NOT NULL,
                    fallback_used BOOLEAN NOT NULL,
                    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
                )
            """)


def record_usage(result: dict) -> None:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO llm_usage (
                    model, input_tokens, output_tokens,
                    estimated_cost_usd, fallback_used
                )
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    result["model"],
                    result["input_tokens"],
                    result["output_tokens"],
                    result["estimated_cost_usd"],
                    result["fallback_used"],
                ),
            )


def get_usage_totals() -> dict:
    with get_connection() as connection:
        with connection.cursor(row_factory=dict_row) as cursor:
            cursor.execute("""
                SELECT
                    COUNT(*) AS requests,
                    COALESCE(SUM(input_tokens), 0) AS input_tokens,
                    COALESCE(SUM(output_tokens), 0) AS output_tokens,
                    COALESCE(SUM(estimated_cost_usd), 0)
                        AS estimated_cost_usd,
                    COUNT(*) FILTER (WHERE fallback_used)
                        AS fallback_requests
                FROM llm_usage
            """)
            return cursor.fetchone()
