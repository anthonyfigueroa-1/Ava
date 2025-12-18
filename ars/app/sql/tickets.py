import psycopg, os, json

from app.logs import logs

db = os.environ["DB"]

def query_closed_tickets() -> list:
    with psycopg.connect(db) as con:
        with con.cursor() as cur:
            cur.execute("""SELECT id::BIGINT, status 
                        FROM tickets 
                        WHERE status = 5
                        AND ((resolution_note_put != 0 
                             AND resolution_note_put < 3)
                             OR resolution_note_put is null)""")
            tickets = cur.fetchall()

    return tickets

def query_one_ticket(id: int):
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

def add_resolution_note(ticket: dict, resolution_note: str, put: int) -> None:
    id = ticket.get("id")

    with psycopg.connect(db) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                        UPDATE tickets
                        SET resolution_note = %s,
                        resolution_note_put = %s
                        WHERE id = %s
                        RETURNING id
                        """,
                        (resolution_note, put, id))

            result = cur.fetchone()

            if not result:
                logs(f"Failed to update resolution note for ticket ID# {id}.")
