import psycopg, os

db = os.getenv("DB")

def create_requesters_table():
    with psycopg.connect(db) as conn:
        with conn.cursor() as cur:
            cur.execute("""CREATE TABLE IF NOT EXISTS requesters (
                id NUMERIC PRIMARY KEY,
                is_agent BOOLEAN,
                vip BOOLEAN,
                first_name TEXT,
                last_name TEXT,
                primary_email TEXT,
                work_phone_number TEXT,
                mobile_phone_number TEXT,
                department_ids TEXT,
                reporting_manager_id TEXT)""")

def add_requesters_table(requester):
    id = requester.get("id")
    is_agent = requester.get("is_agent")
    vip = requester.get("vip_user")
    first_name = requester.get("first_name")
    last_name = requester.get("last_name")
    primary_email = requester.get("primary_email")
    work_phone_number = requester.get("work_phone_number")
    mobile_phone_number = requester.get("mobile_phone_number")
    department_ids = requester.get("department_ids")
    reporting_manager_id = requester.get("reporting_manager_id")

    with psycopg.connect(db, connect_timeout=25) as conn:
        with conn.cursor() as cur:
            try:
                cur.execute("""INSERT INTO requesters 
                            (id, is_agent, vip, first_name, last_name, primary_email, work_phone_number, mobile_phone_number, department_ids, reporting_manager_id)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                            (id, is_agent, vip, first_name, last_name, primary_email, work_phone_number, mobile_phone_number, department_ids, reporting_manager_id))
            except psycopg.errors.UniqueViolation:
                return

def query_requester(id):
    with psycopg.connect(db) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT row_to_json(t) FROM requesters AS t WHERE id = %s", (id,))
            data = cur.fetchone()

        if data:
            return data[0]
        else:
            return None

def combine_requester_name(requester_row: dict) -> str | None:
    if requester_row:
        first_name = requester_row.get("first_name")
        last_name = requester_row.get("last_name")
        id = requester_row.get("id")
        if first_name and last_name:
            full_name = [first_name, last_name]
            full_name = ' '.join(full_name)
            return full_name
        elif first_name and not last_name:
            return first_name
        else:
            return str(id)
