import os, requests
from requests.auth import HTTPBasicAuth
from app.logs import logs
from app.sql.tickets_db import add_time_last_ai_message_post, add_post_email, query_ticket_class
from app.classes.ticket import Ticket

def post_email(ticket_id, ai_response):
    url = f"https://eastwest.freshservice.com/api/v2/tickets/{ticket_id}/reply"
    key = os.environ["FSKEY"]

    header = {
            "Content-Type": "application/json"
            }
    payload = {
            "body": ai_response
            }

    response = requests.post(json=payload, headers=header, url=url, auth=HTTPBasicAuth(key, "x"))

    if response.status_code == 201:
        attempt = 0
        logs(f"Successfully posted AI email to ticket ID# {ticket_id}")
        add_time_last_ai_message_post(ticket_id)
        add_post_email(attempt, ticket_id)

    else:
        logs(f"Failed to post AI email to ticket ID# {ticket_id}")
        logs(f"Querying ticket {ticket_id} for post_email")
        ticket = query_ticket_class(ticket_id)
        attempts = ticket.post_email

        if attempts is None:
            attempts = 1
            add_post_email(attempts, ticket_id)

        else:
            attempts += 1
            add_post_email(attempts, ticket_id)
