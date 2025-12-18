import requests, os
from requests.auth import HTTPBasicAuth
from app.logs import logs

def get_ticket_conversations(ticket: dict) -> dict | None:
    key = os.environ["FSKEY"]
    id = ticket.get("id")
    url = f"https://eastwest.freshservice.com/api/v2/tickets/{id}/conversations"

    try:
        response = requests.get(url, auth=HTTPBasicAuth(key, 'x'), timeout=(5,20))

        if response.status_code != 200:
            logs(f"Failed to fetch conversation for ticket ID# {id} with code {response.status_code}") 

        else:
            conversation = response.json()["conversations"]
            return conversation

    except requests.exceptions.Timeout:
        pass
