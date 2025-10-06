import requests, os
from requests.auth import HTTPBasicAuth
from app.sql.tickets_db import add_conversations

def get_conversations(ticket_id):
    url = f'https://eastwest.freshservice.com/api/v2/tickets/{ticket_id}/conversations'
    key = os.environ["FSKEY"]
    header = {
            "Content-Type": "application/json"
            }

    response = requests.get(headers=header, url=url, auth=HTTPBasicAuth(key, 'x'))

    response = response.json()["conversations"]

    add_conversations(response, ticket_id)    
