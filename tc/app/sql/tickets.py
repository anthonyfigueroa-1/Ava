import psycopg, os, json

from app.logs import logs

db = os.environ["DB"]

def query_open_tickets() -> list:
    with psycopg.connect(db) as con:
        with con.cursor() as cur:
            cur.execute("""SELECT id::BIGINT, status 
                        FROM tickets 
                        WHERE status != 4 OR status != 5 OR status is null""")
            tickets = cur.fetchall()

    return tickets

def update_ticket_table(ticket: dict, conversations: dict | None) -> None:
    id = ticket.get("id")
    status = ticket.get("status")
    priority = ticket.get("priority")
    with psycopg.connect(db) as con:
        with con.cursor() as cur:
            cur.execute("""UPDATE tickets
                        SET conversations = %s, status = %s, priority = %s
                        WHERE id = %s""",
                        (json.dumps(conversations), status, priority, id)
                        )
    if status in (4, 5):
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
                        """,
                        (resolution_note, id))
            
