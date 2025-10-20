import os, requests, json
from requests.auth import HTTPBasicAuth
from app.logs import logs
from app.sql.tickets_db import add_post_note, query_ticket

def post_private_note(ticket_id, ai_response):
    url = f"https://eastwest.freshservice.com/api/v2/tickets/{ticket_id}/notes"
    key = os.environ["FSKEY"]

    header = {
            "Content-Type": "application/json"
            }

    payload = {
            "body": f"USING THIS NOTE FOR AI TESTING<br><br>email:<br>{ai_response.get('email')}<br><br>note:<br>{ai_response.get('note')}"
            }

    response = requests.post(url=url, json=payload, headers=header, auth=HTTPBasicAuth(key, 'X'))

    if response.status_code == 201:
        attempt = 0
        logs(f"Successfully posted AI note to ticket ID# {ticket_id}")
        add_post_note(attempt, ticket_id)

    else:
        logs(f"Failed to post AI note to ticket ID# {ticket_id} with status code of {response.status_code}")
        error = response.json()
        logs(json.dumps(error, indent=4))
        logs(f"Querying ticket {ticket_id} for post_note")
        ticket = query_ticket(ticket_id)
        attempts = ticket.get("post_note")

        if attempts is None:
            attempts = 1
            add_post_note(attempts, ticket_id)

        else:
            attempts += 1
            add_post_note(attempts, ticket_id)
