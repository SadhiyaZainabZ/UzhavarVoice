
import os

import psycopg
from psycopg.rows import dict_row


def get_connection():
    database_url = os.getenv("DATABASE_URL", "")

    if not database_url:
        raise RuntimeError("DATABASE_URL is not configured")

    return psycopg.connect(
        database_url,
        connect_timeout=5,
        row_factory=dict_row,
    )


def check_database() -> bool:
    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                return cursor.fetchone() is not None
    except Exception:
        return False


def initialize_usage_table() -> None:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS llm_usage (
                    id BIGSERIAL PRIMARY KEY,
                    model TEXT NOT NULL,
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
                    model,
                    input_tokens,
                    output_tokens,
                    estimated_cost_usd,
                    fallback_used
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
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT
                    COUNT(*) AS requests,
                    COALESCE(SUM(input_tokens), 0) AS input_tokens,
                    COALESCE(SUM(output_tokens), 0) AS output_tokens,
                    COALESCE(SUM(estimated_cost_usd), 0)
                        AS estimated_cost_usd,
                    COALESCE(
                        SUM(CASE WHEN fallback_used THEN 1 ELSE 0 END),
                        0
                    ) AS fallback_requests
                FROM llm_usage
            """)

            return cursor.fetchone()
from pgvector import Vector


def initialize_document_chunks_table() -> None:
    """Create the pgvector table for agricultural document chunks."""

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("CREATE EXTENSION IF NOT EXISTS vector")

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS document_chunks (
                    id BIGSERIAL PRIMARY KEY,
                    content_hash TEXT UNIQUE NOT NULL,
                    chunk_text TEXT NOT NULL,
                    source TEXT NOT NULL,
                    file_type TEXT NOT NULL,
                    page INTEGER,
                    heading TEXT,
                    extraction_method TEXT NOT NULL,
                    embedding VECTOR(768) NOT NULL,
                    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
                )
            """)


def store_document_chunk(chunk: dict, embedding: list[float]) -> None:
    """Store one chunk and its embedding without creating duplicates."""

    import hashlib

    if len(embedding) != 768:
        raise ValueError("Embedding must contain exactly 768 dimensions")

    content_hash = hashlib.sha256(
        (
            chunk["source"]
            + str(chunk.get("page"))
            + str(chunk.get("heading"))
            + chunk["text"]
        ).encode("utf-8")
    ).hexdigest()

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO document_chunks (
                    content_hash,
                    chunk_text,
                    source,
                    file_type,
                    page,
                    heading,
                    extraction_method,
                    embedding
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (content_hash) DO NOTHING
                """,
                (
                    content_hash,
                    chunk["text"],
                    chunk["source"],
                    chunk["file_type"],
                    chunk.get("page"),
                    chunk.get("heading"),
                    chunk["extraction_method"],
                    Vector(embedding),
                ),
            )


def store_document_chunks(
    chunks: list[dict],
    embeddings: list[list[float]],
) -> int:
    """Store multiple document chunks and embeddings in one database connection."""

    import hashlib
    from pgvector import Vector
    from pgvector.psycopg import register_vector

    if len(chunks) != len(embeddings):
        raise ValueError("Chunks and embeddings must have the same length")

    if not chunks:
        return 0

    rows = []

    for chunk, embedding in zip(chunks, embeddings, strict=True):
        if len(embedding) != 768:
            raise ValueError("Each embedding must contain exactly 768 dimensions")

        content_hash = hashlib.sha256(
            (
                chunk["source"]
                + str(chunk.get("page"))
                + str(chunk.get("heading"))
                + chunk["text"]
            ).encode("utf-8")
        ).hexdigest()

        rows.append((
            content_hash,
            chunk["text"],
            chunk["source"],
            chunk["file_type"],
            chunk.get("page"),
            chunk.get("heading"),
            chunk["extraction_method"],
            Vector(embedding),
        ))

    query = """
        INSERT INTO document_chunks (
            content_hash,
            chunk_text,
            source,
            file_type,
            page,
            heading,
            extraction_method,
            embedding
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (content_hash) DO NOTHING
    """

    with get_connection() as connection:
        register_vector(connection)

        with connection.cursor() as cursor:
            cursor.executemany(query, rows)
            inserted_count = cursor.rowcount

    return inserted_count


def get_existing_chunk_hashes(chunks: list[dict]) -> set[str]:
    """Return hashes of chunks that are already stored in PostgreSQL."""

    import hashlib

    if not chunks:
        return set()

    hashes = []

    for chunk in chunks:
        content_hash = hashlib.sha256(
            (
                chunk["source"]
                + str(chunk.get("page"))
                + str(chunk.get("heading"))
                + chunk["text"]
            ).encode("utf-8")
        ).hexdigest()

        hashes.append(content_hash)

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT content_hash
                FROM document_chunks
                WHERE content_hash = ANY(%s)
                """,
                (hashes,),
            )

            return {row["content_hash"] for row in cursor.fetchall()}
