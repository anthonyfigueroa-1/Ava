import requests, os
from requests.auth import HTTPBasicAuth
from app.logs import logs

key = os.environ["FSKEY"]

def get_convo(ticket_id) -> list | None:
    url = f"https://eastwest.freshservice.com/api/v2/tickets/{ticket_id}/conversations"
    
    try:
        response = requests.get(url, auth=HTTPBasicAuth(key, 'x'), timeout=(20,20))

        if response.status_code != 200:
            logs(f"Failed to GET convos ticket ID# {ticket_id} with status code of {response.status_code}")
        else:
            return response.json()["conversations"]

    except requests.Timeout:
        logs(f"Request to GET convos ticket ID# {ticket_id} timed out") 
