import requests, os, json
from requests.auth import HTTPBasicAuth
from app.sql.tickets_db import add_put_fields, query_ticket

def put_fields(ticket_id):
    ticket = query_ticket(ticket_id)
    ticket_json = ticket.get("json")
    ticket_json = json.loads(ticket_json)
    tags = ticket_json.get("tags", None)
    responder_id = ticket_json.get("responder_id", None)
    
    if not tags:
        tags = ["T1", "AI"]
    else:
        tags.append("AI")

    url = f"https://eastwest.freshservice.com/api/v2/tickets/{ticket_id}"
    key = os.environ["FSKEY"]

    header = {
            "Content-Type": "application/json"
            }

    payload = {
            "responder_id": responder_id,
            "tags": tags
            }

    response = requests.put(url=url, headers=header, json=payload, auth=HTTPBasicAuth(key, "X"))

    if response.status_code == 200:
        add_put_fields(0, ticket_id)

    else:
        attempts = ticket.get("put_fields")

        if not attempts:
            attempts = 1

            add_put_fields(attempts, ticket_id)

        else:
            attempts += 1

            add_put_fields(attempts, ticket_id)
