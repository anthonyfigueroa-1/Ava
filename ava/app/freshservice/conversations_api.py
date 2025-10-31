import requests, os, json
from requests.auth import HTTPBasicAuth
from app.sql.tickets_db import add_conversations
from app.logs import logs

def get_conversations(ticket_id):
    try:
        url = f'https://eastwest.freshservice.com/api/v2/tickets/{ticket_id}/conversations'
        key = os.environ["FSKEY"]
        header = {
            "Content-Type": "application/json"
            }

        response = requests.get(headers=header, url=url, auth=HTTPBasicAuth(key, 'x'), timeout=(5, 20))

        if response.status_code != 200:
            text = f"Could not fetch conversations from FS for ticket ID# {ticket_id}"
            logs(text)

            add_conversations(text, ticket_id)

        else:
            response = response.json()["conversations"]

            add_conversations(response, ticket_id)    

    except requests.exceptions.ReadTimeout:
        logs(f"Timeout Error for getting converstations for ticket ID# {ticket_id}")
        pass
