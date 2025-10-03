import psycopg

def create_db():
    postgres = "postgresql://anthony:Pock!00!@localhost:5432/postgres"

    with psycopg.connect(postgres) as conn:
        conn.autocommit = True
        with conn.cursor() as cur:
            try:
                cur.execute("""CREATE DATABASE air;""")
            except psycopg.errors.DuplicateDatabase:
                pass
