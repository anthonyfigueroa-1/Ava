import requests, os, json
from requests.auth import HTTPBasicAuth
from app.logs import logs
from app.sql.tickets_db import add_json

def get_tickets():
    url = f'https://eastwest.freshservice.com/api/v2/tickets/filter?query="group_id:{os.environ["ITGROUP"]}"' 
    key = os.environ["FSKEY"]

    response = requests.get(url, auth=HTTPBasicAuth(key, "X"))
    tickets = response.json()["tickets"]

    if response.status_code == 200:
        logs("Got batch of tickets for group ALL IT")

    return tickets

def get_one_ticket(ticket_id, test=False):
    url = f'https://eastwest.freshservice.com/api/v2/tickets/{ticket_id}'
    key = os.environ["FSKEY"]

    response = requests.get(url, auth=HTTPBasicAuth(key, "X"))

    if response.status_code != 200:
        logs(f"Something went wrong getting ticket ID# {ticket_id}")
        response = response.json()
        logs(json.dumps(response, indent=4))

    else:
        ticket = response.json()["ticket"]
        if test is True:
            return ticket

        add_json(ticket)

