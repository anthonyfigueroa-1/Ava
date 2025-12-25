import requests, os
from requests.auth import HTTPBasicAuth
from app.logs import logs

key = os.environ["FSKEY"]

def get_ticket(ticket_id):
    url = f"https://eastwest.freshservice.com/api/v2/tickets/{ticket_id}"
    
    try:
        response = requests.get(url, auth=HTTPBasicAuth(key, 'x'), timeout=(20,20))

        if response.status_code != 200:
            logs(f"Failed to GET ticket ID# {ticket_id} with status code of {response.status_code}")
        else:
            return response.json()["ticket"]

    except requests.Timeout:
        logs(f"Request to GET ticket ID# {ticket_id} timed out") 
