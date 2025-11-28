import psycopg, json, os
import time as dtime
from datetime import datetime
from psycopg.types.json import Jsonb

from app.freshservice.requesters_api import get_requester
from app.sql.requesters_db import query_requester
from app.sql.departments_db import query_departments_table
from app.logs import logs

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
                raw_description TEXT,
                ai_email TEXT,
                ai_note TEXT,
                ai_next_steps TEXT,
                ai_attempts BIGINT,
                conversations TEXT,
                ticket_created BIGINT,
                time_last_ai_message_post BIGINT,
                put_fields BIGINT,
                status BIGINT,
                priority BIGINT,
                json TEXT)""")

def add_tickets_table(tickets):
    if isinstance(tickets, dict):
        tickets = [tickets]

    with psycopg.connect(tickets_db) as conn:
        with conn.cursor() as cur:
            for ticket in tickets:
                id = ticket.get("id")
                subject = ticket.get("subject")
                description = ticket.get("description_text")
                department = query_departments_table(ticket.get("department_id"))
                raw_description = ticket.get("description")
                priority = ticket.get("priority")
                status = ticket.get("status")

                #enter time as UNIX time
                time = datetime.strptime(ticket.get("created_at"), "%Y-%m-%dT%H:%M:%SZ")
                unixtime = time.timestamp()

                cur.execute("""INSERT INTO tickets 
                            (id, department, subject, description, raw_description, ticket_created, json, priority, status) 
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                            ON CONFLICT (id) DO NOTHING
                            RETURNING id;""",
                            (id, department, subject, description, raw_description, unixtime, Jsonb(ticket), priority, status))

                result = cur.fetchone()

                if not result:
                    update_ticket(ticket)



def add_ai_response(ai_response, attempts, id):
    ai_email = ai_response.get("email")
    ai_email = {
            "ai_email": ai_email,
            "attempts": None
                }
    ai_note = ai_response.get("note")
    ai_note = {
            "ai_note": ai_note,
            "attempts": None
            }
    ai_next_steps = ai_response.get("next_steps")
    ai_next_steps = {
            "ai_next_steps": ai_next_steps,
            "attempts": None
            }

    with psycopg.connect(tickets_db) as conn:
        with conn.cursor() as cur:
            cur.execute("UPDATE tickets SET ai_email = %s, ai_note = %s, ai_next_steps = %s, ai_attempts = %s WHERE id = %s;",
                        (Jsonb(ai_email), Jsonb(ai_note), Jsonb(ai_next_steps), attempts, id))
    logs(f"Updated ticket ID# {id} ai_email, ai_note, ai_next_steps and ai_attempts fields")

def add_conversations(conversations, id):
    with psycopg.connect(tickets_db) as conn:
        with conn.cursor() as cur:
            cur.execute("UPDATE tickets SET conversations = %s WHERE id = %s", (Jsonb(conversations), id))

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

def add_json(ticket):
    id = ticket.get("id")

    with psycopg.connect(tickets_db) as conn:
        with conn.cursor() as cur:
            cur.execute("UPDATE tickets SET json = %s WHERE id = %s", (json.dumps(ticket), id))

    logs(f"Updated ticket ID# {id} json field")

def add_requester(ticket):
    ticket_id = ticket.get("id")
    requester_id = ticket.get("requester_id")

    tries = 1
    while True:
        if tries == 2:
            get_requester(ticket)
            requester = query_requester(requester_id)

            if not requester:
                requester_email = None
                requester_name = None
                vip = None
                break

        else:
            requester = query_requester(requester_id)
            tries += 1

        if requester:
            requester_email = requester.get("primary_email")
            first_name = requester.get("first_name", "NAME NOT FOUND")
            last_name = requester.get("last_name")
            vip = requester.get("vip")
            requester_name = [first_name if first_name else "NAME NOT FOUND", last_name if last_name else ""]
            requester_name = ' '.join(requester_name)
            break
    
    with psycopg.connect(tickets_db) as conn:
        with conn.cursor() as cur:
            cur.execute("""UPDATE tickets SET requester_name = %s, requester_email = %s, requester_vip = %s
                        WHERE id = %s AND requester_email is NULL
                        """, (requester_name, requester_email, vip, ticket_id))

def add_service_request(items, id):
    with psycopg.connect(tickets_db) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                        UPDATE tickets SET service_request = %s WHERE id = %s
                        """, (Jsonb(items), id))

def add_metadata(metadata, id):
    with psycopg.connect(tickets_db) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                        UPDATE tickets SET metadata = %s WHERE id = %s
                        """, (Jsonb(metadata), id))

def update_ticket(ticket):
    id = ticket.get("id")
    priority = ticket.get("priority")
    status = ticket.get("status")

    with psycopg.connect(tickets_db) as conn:
        with conn.cursor() as cur:
            cur.execute("UPDATE tickets SET priority = %s, status = %s WHERE id = %s", (priority, status, id))


def update_ai_email(id, ai_email):
   with psycopg.connect(tickets_db) as conn:
        with conn.cursor() as cur:
            cur.execute("""UPDATE tickets SET ai_email = %s WHERE id = %s""", (json.dumps(ai_email), id))

def update_ai_note(id, ai_note):
   with psycopg.connect(tickets_db) as conn:
        with conn.cursor() as cur:
            cur.execute("""UPDATE tickets SET ai_note = %s WHERE id = %s""", (json.dumps(ai_note), id))

def update_ai_next_steps(id, ai_next_steps):
   with psycopg.connect(tickets_db) as conn:
        with conn.cursor() as cur:
            cur.execute("""UPDATE tickets SET ai_next_steps = %s WHERE id = %s""", (json.dumps(ai_next_steps), id))

def update_ai_attempts(id: int, attempts: int) -> None:
    with psycopg.connect(tickets_db) as conn:
        with conn.cursor() as cur:
            cur.execute("UPDATE tickets SET ai_attempts = %s WHERE id = %s", (attempts, id))

def query_ai_response(id):
    with psycopg.connect(tickets_db) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT ai_email FROM tickets WHERE id = %s", (id,))
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

    else:
        data = None
        logs(f"Was not able to find ticket ID# {id} in tickets table")

    return data

def query_ticket_response(id):
    with psycopg.connect(tickets_db) as conn:
        with conn.cursor() as cur:
            cur.execute("""SELECT row_to_json(t)
                        FROM (
                            SELECT id, priority, requester_name, requester_email, requester_vip, department, subject, raw_description, service_request, conversations
                            FROM tickets
                            WHERE id = %s
                            ) AS t""", (id,))
            data = cur.fetchone()
    if data:
        data = data[0]

    else:
        data = None
        logs(f"Was not able to find ticket ID# {id} in tickets table")

    return data

def query_tickets_ai_slim(keywords: list[str], id: int, requester_email: str, limit: int) -> list | None:
    query = f"""
    WITH keywords AS (
            SELECT unnest(%s::text[]) as keyword
            ),
    cleaned as (
            SELECT t.id,
                    t.requester_name,
                    t.requester_email,
                    regexp_replace(t.subject, E'[\\r\\n]+', ' ', 'g') as subject_clean,
                    regexp_replace(t.description, E'[\\r\\n]+', ' ', 'g') as description_clean
            FROM tickets t),
    matches as (
            SELECT c.*,
                    SUM(word_similarity(c.description_clean, keyword) + word_similarity(c.subject_clean, keyword)) as score
                FROM cleaned c
                LEFT JOIN LATERAL (
                    SELECT keyword FROM keywords
                    WHERE c.description_clean ILIKE keyword
                    OR c.subject_clean ILIKE keyword
                    ) match_table ON TRUE
                GROUP BY c.id, c.requester_name, c.requester_email, c.subject_clean, c.description_clean
                )
                SELECT row_to_json(t)
                FROM matches
                AS t
                WHERE id != %s AND score IS NOT null
                ORDER BY (CASE WHEN requester_email = %s THEN 1 ELSE 0 END) DESC,
                COALESCE(score, 0) DESC
                LIMIT %s;
    """

    keywords = [f"%{keyword}%" for keyword in keywords]

    with psycopg.connect(tickets_db) as conn:
        with conn.cursor() as cur:
            cur.execute(query, [keywords, id, requester_email, limit])
            data = cur.fetchall()

    if data is None:
        logs(f"Was not able to find any relevant tickets to ticket ID# {id} in tickets table")

    else:
        return data

def query_tickets_ai(ids: list[int]) -> list | None:
    clause = " OR ".join(f"id = %s" for _ in ids)
    query = f"""SELECT row_to_json(t)
                        FROM (
                            SELECT id, requester_name, requester_email, department, subject, raw_description, conversations
                            FROM tickets
                            WHERE ({clause})
                            )
                        AS t"""

    with psycopg.connect(tickets_db) as conn:
        with conn.cursor() as cur:
            cur.execute(query, [*ids])
            data = cur.fetchall()
    if data:
        return data

    else:
        #Needs to be reworded
        logs(f"Could not succesfully find ticket IDs {ids}")
