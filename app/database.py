import os

import psycopg


def check_database() -> bool:
    database_url = os.getenv("DATABASE_URL", "")

    if not database_url:
        return False

    try:
        with psycopg.connect(database_url, connect_timeout=3) as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                return cursor.fetchone() == (1,)
    except Exception:
        return False
