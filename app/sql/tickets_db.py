import psycopg, json 
import time as dtime
from datetime import datetime

from app.sql.requesters_db import query_name_requesters_table, query_requester
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
                last_ai_gen TEXT,
                conversations TEXT,
                ticket_created BIGINT,
                time_last_message_recieved BIGINT,
                time_last_ai_message_post BIGINT,
                closed BOOLEAN,
                json TEXT)""")

def add_tickets_table(ticket):
    id = ticket.get("id")
    subject = ticket.get("subject")
    description = ticket.get("description_text")
    requester_name = query_name_requesters_table(ticket.get("requester_id"))
    department = query_departments_table(ticket.get("department_id"))

    #enter time as UNIX time
    time = datetime.strptime(ticket.get("created_at"), "%Y-%m-%dT%H:%M:%SZ")
    unixtime = time.timestamp()

    #get requester_email
    requester = query_requester(ticket.get("requester_id"))
    if requester:
        requester_email = requester.get("primary_email")
    else:
        requester_email = None

    with psycopg.connect(tickets_db) as conn:
        with conn.cursor() as cur:
            try:
                cur.execute("""INSERT INTO tickets 
                            (id, requester_name, requester_email, department, subject, description, ticket_created, json) 
                            VALUES (%s, %s, %s, %s, %s, %s, %s);""",
                            (id, requester_name, requester_email, department, subject, description, unixtime, json.dumps(ticket)))
                logs(f"Ticket ID# {id} added tickets table")
            except psycopg.errors.UniqueViolation:
                logs(f"Ticket ID# {id} already in tickets table")

def add_ai_response(ai_response, id):
    with psycopg.connect(tickets_db) as conn:
        with conn.cursor() as cur:
            cur.execute("UPDATE tickets SET last_ai_gen = %s WHERE id = %s;",
                        (ai_response, id))
    logs(f"Updated ticket ID# {id} last_ai_gen field.")

def add_conversations(conversations, id):
    with psycopg.connect(tickets_db) as conn:
        with conn.cursor() as cur:
            cur.execute("UPDATE tickets SET conversations = %s WHERE id = %s", (json.dumps(conversations, indent=4), id))

    logs(f"Updated ticket ID# {id} conversations field")

def query_ai_response(id):
    with psycopg.connect(tickets_db) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT last_ai_gen FROM tickets WHERE id = %s", (id,))
            ai_response = cur.fetchone()

            return ai_response 

def query_ticket(id):
    with psycopg.connect(tickets_db) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT row_to_json(t) FROM tickets AS t WHERE id = %s", (id,))
            data = cur.fetchone()
    if data:
        data = data[0]
        #getting rid of json as it is not needed
        data["json"] = None
        logs(f"Found {id} in tickets table, returning row")
    else:
        data = None
        logs(f"Was not able to find {id} in tickets table")

    return data
