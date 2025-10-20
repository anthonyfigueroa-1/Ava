import requests, os, json
from requests.auth import HTTPBasicAuth
from app.sql.tickets_db import add_conversations
from app.logs import logs

def get_conversations(ticket_id):
    url = f'https://eastwest.freshservice.com/api/v2/tickets/{ticket_id}/conversations'
    key = os.environ["FSKEY"]
    header = {
            "Content-Type": "application/json"
            }

    response = requests.get(headers=header, url=url, auth=HTTPBasicAuth(key, 'x'))

    if response.status_code == 200:
        response = response.json()["conversations"]

        add_conversations(response, ticket_id)    

    else:
        text = f"Could not fetch conversations from FS for ticket ID# {ticket_id}"

        logs(text)
        
        response = response.json()

        logs(json.dumps(response, indent=4))

        add_conversations(text, ticket_id)
