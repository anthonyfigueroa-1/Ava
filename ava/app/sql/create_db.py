import psycopg, os

def create_db():
    db = os.getenv("PG")

    with psycopg.connect(db, connect_timeout=25) as conn:
        conn.autocommit = True
        with conn.cursor() as cur:
            try:
                cur.execute("""CREATE DATABASE air;""")
            except psycopg.errors.DuplicateDatabase:
                pass
