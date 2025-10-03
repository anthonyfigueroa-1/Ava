import psycopg, json

from app.sql.requesters_db import query_name_requesters_table
from app.sql.departments_db import query_departments_table
from app.logs import logs

tickets_db = "postgresql://anthony:Pock!00!@localhost:5432/air"

def create_tickets_table():
    with psycopg.connect(tickets_db) as conn:
        with conn.cursor() as cur:
            cur.execute("""CREATE TABLE IF NOT EXISTS tickets(
                id NUMERIC PRIMARY KEY,
                requester_name TEXT,
                requester_email TEXT,
                department TEXT,
                subject TEXT,
                description TEXT,
                first_response TEXT,
                private_note TEXT,
                time_recieved BIGINT,
                time_message_post BIGINT,
                json TEXT)""")

def add_tickets_table(ticket):
    id = ticket.get("id")
    subject = ticket.get("subject")
    description = ticket.get("description_text")
    requester_name = query_name_requesters_table(ticket.get("requester_id"))
    requester_email = ticket.get("email")
    department = query_departments_table(ticket.get("department_id"))

    with psycopg.connect(tickets_db) as conn:
        with conn.cursor() as cur:
            try:
                cur.execute("""INSERT INTO tickets 
                            (id, requester_name, requester_email, department, subject, description, json) 
                            VALUES (%s, %s, %s, %s, %s, %s, %s);""",
                            (id, requester_name, requester_email, department, subject, description, json.dumps(ticket)))
                logs(f"Ticket ID# {id} added tickets database")
            except psycopg.errors.UniqueViolation:
                logs(f"Ticket ID# {id} already in tickets database")

def add_ai_response(ai_response, id):
    email, note = ai_response
    
    with psycopg.connect(tickets_db) as conn:
        with conn.cursor() as cur:
            cur.execute("UPDATE tickets SET first_response = %s, private_note = %s WHERE id = %s AND first_response is NULL AND private_note is NULL;",
                        (email, note, id))
            logs(f"Ticket ID# {id} updated 'first response' and private note' fields")

def query_ai_response(id):
    with psycopg.connect(tickets_db) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT first_response, private_note FROM tickets WHERE id = %s", (id,))
            ai_response = cur.fetchone()

            return ai_response 
