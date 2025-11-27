import requests, json, os
from requests.auth import HTTPBasicAuth

from app.logs import logs
from app.sql.tickets_db import add_service_request

def get_service_request_info(ticket: dict) -> None:
    ticket_id = ticket.get("id")
    url = f'https://eastwest.freshservice.com/api/v2/tickets/{ticket_id}/requested_items'
    key = os.environ["FSKEY"]

    try:
        response = requests.get(url, auth=HTTPBasicAuth(key, "X"), timeout=(20,20)) 

        if response.status_code != 200:
           logs(f"Failed to get service request info from ticket {ticket_id} with HTTP code of {response.status_code}")
        else:
            requested_items = response.json()["requested_items"]
            add_service_request(requested_items, ticket_id)

    except requests.Timeout:
        logs(f"Request for getting items of service request for {ticket_id} timed out")
