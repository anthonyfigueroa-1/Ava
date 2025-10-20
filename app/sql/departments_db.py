import psycopg, os

db = os.getenv("DB")

def create_departments_table():
    with psycopg.connect(db) as conn:
        with conn.cursor() as cur:
            cur.execute("""CREATE TABLE IF NOT EXISTS departments (
                id NUMERIC PRIMARY KEY,
                name TEXT)""")

def add_departments_table(department):
    id = department.get("id")
    name = department.get("name")
    try:
        with psycopg.connect(db) as conn:
            with conn.cursor() as cur:
                cur.execute("INSERT INTO departments (id, name) VALUES (%s, %s)", (id, name))
    except psycopg.errors.UniqueViolation:
        return

def query_departments_table(id):
    if not id:
        return None
    with psycopg.connect(db) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT name FROM departments WHERE id = %s", (id,))
            data = cur.fetchone()

            if data:
                name = data[0]

                return name
            else:
                return None
