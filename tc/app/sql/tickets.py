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
    with psycopg.connect(db) as con:
        with con.cursor() as cur:
            cur.execute("""UPDATE tickets
                        SET conversations = %s, status = %s
                        WHERE id = %s""",
                        (json.dumps(conversations), status, id)
                        )
    logs(f"Successfully updated conversations and status of ticket ID# {id} in database")
