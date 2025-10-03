import psycopg

db = "postgresql://anthony:Pock!00!@localhost:5432/air"

def create_requesters_table():
    with psycopg.connect(db) as conn:
        with conn.cursor() as cur:
            cur.execute("""CREATE TABLE IF NOT EXISTS requesters (
                id NUMERIC PRIMARY KEY,
                is_agent BOOLEAN,
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
    first_name = requester.get("first_name")
    last_name = requester.get("last_name")
    primary_email = requester.get("primary_email")
    work_phone_number = requester.get("work_phone_number")
    mobile_phone_number = requester.get("mobile_phone_number")

    with psycopg.connect(db) as conn:
        with conn.cursor() as cur:
            try:
                cur.execute("""INSERT INTO requesters (id, is_agent, first_name, last_name, primary_email, work_phone_number, mobile_phone_number)
                            VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                            (id, is_agent, first_name, last_name, primary_email, work_phone_number, mobile_phone_number))
            except psycopg.errors.UniqueViolation:
                return

def query_name_requesters_table(id):
    with psycopg.connect(db) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT first_name, last_name FROM requesters WHERE id = %s", (id,))
            full_name = cur.fetchone()
            if full_name:
                #This if checks to make sure if there is a last name, if last name is not None/NULL, it will combine the tuple values into one and return both first and last name.
                if full_name[1]:    
                    full_name = " ".join(map(str, full_name))
                    return full_name
                else:
                    full_name = full_name[0]
                    return full_name
