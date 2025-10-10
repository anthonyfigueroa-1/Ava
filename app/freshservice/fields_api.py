import requests, os
from requests.auth import HTTPBasicAuth
from app.sql.tickets_db import add_put_fields, query_ticket_class
from app.classes.ticket import Ticket

def put_fields(ticket_id):
    url = f"https://eastwest.freshservice.com/api/v2/tickets/{ticket_id}"
    key = os.environ["FSKEY"]

    header = {
            "Content-Type": "application/json"
            }

    payload = {
            "responder_id": None,
            "tags": ["T1", "AI"]
            }

    response = requests.put(url=url, headers=header, json=payload, auth=HTTPBasicAuth(key, "X"))

    if response.status_code == 200:
        add_put_fields(0, ticket_id)

    else:
        ticket = query_ticket_class(ticket_id)
        attempts = ticket.put_fields

        if not attempts:
            attempts = 1

            add_put_fields(attempts, ticket_id)

        else:
            attempts += 1

            add_put_fields(attempts, ticket_id)
