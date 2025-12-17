import psycopg, os, json

from app.logs import logs

db = os.environ["DB"]

def query_open_tickets() -> list:
    with psycopg.connect(db) as con:
        with con.cursor() as cur:
            cur.execute("""SELECT id::BIGINT, status 
                        FROM tickets 
                        WHERE status != 5 OR status is null""")
            tickets = cur.fetchall()

    return tickets

def query_one_ticket(ticket):
    id = ticket.get("id")
    with psycopg.connect(db) as con:
        with con.cursor() as cur:
            cur.execute("""SELECT row_to_json(t) FROM tickets
                        AS t
                        WHERE id = %s""",
                        (id,))

            row = cur.fetchone()

    if row:
        row = row[0]

        return row

def update_ticket_table(ticket: dict, conversations: dict | None) -> None:
    id = ticket.get("id")
    status = ticket.get("status")
    priority = ticket.get("priority")
    with psycopg.connect(db) as con:
        with con.cursor() as cur:
            cur.execute("""UPDATE tickets
                        SET conversations = %s, status = %s, priority = %s
                        WHERE id = %s
                        """,
                        (json.dumps(conversations), status, priority, id)
                        )
    if status == 4:
        logs(f"Successfully updated conversations and resolved ticket ID# {id} in database")
    if status == 5:
        logs(f"Successfully updated conversations and closed ticket ID# {id} in database")

def add_resolution_note(ticket: dict, resolution_note: str) -> None:
    id = ticket.get("id")

    with psycopg.connect(db) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                        UPDATE tickets
                        SET resolution_note = %s
                        WHERE id = %s
                        AND resolution_note is NULL
                        RETURNING id
                        """,
                        (resolution_note, id))

            result = cur.fetchone()

            if not result:
                logs(f"Failed to update resolution note for ticket ID# {id}.")
