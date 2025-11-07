import requests, os
from requests.auth import HTTPBasicAuth
from app.logs import logs

key = os.environ["FSKEY"]

def get_one_ticket(ticket_id: int) -> dict | None:
    url = f"https://eastwest.freshservice.com/api/v2/tickets/{ticket_id}"

    try:
        response = requests.get(url, auth=HTTPBasicAuth(key, "x"), timeout=(5,20))

        if response.status_code != 200:
            logs(f"Failed to fetch ticket ID# {ticket_id} with code {response.status_code}") 
            return

        else:
            ticket = response.json()["ticket"]

            return ticket

    except requests.exceptions.Timeout:
        logs(f"Timeout error for ticket ID# {ticket_id}")
        return

