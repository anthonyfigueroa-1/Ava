import psycopg, json, os
import time as dtime
from datetime import datetime

from app.sql.requesters_db import query_name_requesters_table, query_requester
from app.sql.departments_db import query_departments_table
from app.logs import logs
from app.classes.ticket import Ticket

tickets_db = os.getenv("DB")

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
                ai_attempts BIGINT,
                conversations TEXT,
                ticket_created BIGINT,
                time_last_message_recieved BIGINT,
                time_last_ai_message_post BIGINT,
                post_email BIGINT,
                post_note BIGINT,
                put_fields BIGINT,
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
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s);""",
                            (id, requester_name, requester_email, department, subject, description, unixtime, json.dumps(ticket)))
                logs(f"Ticket ID# {id} added tickets table")
            except psycopg.errors.UniqueViolation:
                logs(f"Ticket ID# {id} already in tickets table")

def add_ai_response(ai_response, attempts, id):
    with psycopg.connect(tickets_db) as conn:
        with conn.cursor() as cur:
            cur.execute("UPDATE tickets SET last_ai_gen = %s, ai_attempts = %s WHERE id = %s;",
                        (ai_response, attempts, id))
    logs(f"Updated ticket ID# {id} last_ai_gen and ai_attempts fields")

def add_conversations(conversations, id):
    with psycopg.connect(tickets_db) as conn:
        with conn.cursor() as cur:
            cur.execute("UPDATE tickets SET conversations = %s WHERE id = %s", (json.dumps(conversations), id))

    logs(f"Updated ticket ID# {id} conversations field")

def add_time_last_ai_message_post(id):
    unix_time = dtime.time()

    with psycopg.connect(tickets_db) as conn:
        with conn.cursor() as cur:
            cur.execute("UPDATE tickets SET time_last_ai_message_post = %s WHERE id = %s", (unix_time, id))

    logs(f"Updated ticket ID# {id} time_last_ai_message_post field")

def add_post_email(attempts, id):
    with psycopg.connect(tickets_db) as conn:
        with conn.cursor() as cur:
            cur.execute("UPDATE tickets SET post_email = %s WHERE id = %s", (attempts, id))

    logs(f"Updated ticket ID# {id} post_email field")

def add_post_note(attempts, id):
    with psycopg.connect(tickets_db) as conn:
        with conn.cursor() as cur:
            cur.execute("UPDATE tickets SET post_note = %s WHERE id = %s", (attempts, id))

    logs(f"Updated ticket ID# {id} post_note field")

def add_put_fields(attempts, id):
    with psycopg.connect(tickets_db) as conn:
        with conn.cursor() as cur:
            cur.execute("UPDATE tickets SET put_fields = %s WHERE id = %s", (attempts, id))

    logs(f"Updated ticket ID# {id} put_fields field")

def query_ai_response(id):
    with psycopg.connect(tickets_db) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT last_ai_gen FROM tickets WHERE id = %s", (id,))
            ai_response = cur.fetchone()

            return ai_response 

def query_time_last_ai_message_post(id):
    with psycopg.connect(ticket_db) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT time_last_ai_message_post FROM tickets WHERE id = %s", (id,))
            data = cur.fetchone()
    if data:
        time = data[0]
        return time

    return data

def query_ticket(id):
    with psycopg.connect(tickets_db) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT row_to_json(t) FROM tickets AS t WHERE id = %s", (id,))
            data = cur.fetchone()
    if data:
        data = data[0]
        #getting rid of json as it is not needed
        data["json"] = None
        logs(f"Found ticket ID# {id} in tickets table, returning row as a json")
    else:
        data = None
        logs(f"Was not able to find ticket ID# {id} in tickets table")

    return data

def query_ticket_class(id):
    with psycopg.connect(tickets_db) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT row_to_json(t) FROM tickets AS t WHERE id = %s", (id,))
            data = cur.fetchone()
    if data:
        data = data[0]
        logs(f"Found ticket ID# {id} in tickets table, returning row as a class")
        ticket = Ticket(
                data.get("id"),
                data.get("requester_name"),
                data.get("requester_email"),
                data.get("department"),
                data.get("subject"),
                data.get("description"),
                data.get("last_ai_gen"),
                data.get("ai_attempts"),
                data.get("conversations"),
                data.get("ticket_created"),
                data.get("time_last_message_recieved"),
                data.get("time_last_ai_message_post"),
                data.get("post_email"),
                data.get("post_note"),
                data.get("put_fields"),
                data.get("closed"))

        return ticket

    else:
        logs(f"Was not able to find ticket ID# {id} in tickets table")   
        return None

