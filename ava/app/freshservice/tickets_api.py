import requests, os, json
from requests.auth import HTTPBasicAuth
from app.logs import logs
from app.sql.tickets_db import add_json

def get_tickets():
    try:
        url = f'https://eastwest.freshservice.com/api/v2/tickets/filter?query="group_id:{os.environ["ITGROUP"]}"' 
        key = os.environ["FSKEY"]

        response = requests.get(url, auth=HTTPBasicAuth(key, "X"))

        if response.status_code != 200:
            logs("Something went wrong getting batch of tickets.")
            logs(f"Status code: {response.status_code}")

        else:
            tickets = response.json()["tickets"]
            logs("Got batch of tickets for group ALL IT")
            return tickets

    except requests.exceptions.ReadTimeout:
        logs("Timeout Error for getting batch of tickets occured")

def get_one_ticket(ticket_id):
    url = f'https://eastwest.freshservice.com/api/v2/tickets/{ticket_id}?include=tags'
    key = os.environ["FSKEY"]

    response = requests.get(url, auth=HTTPBasicAuth(key, "X"))

    if response.status_code != 200:
        logs(f"Something went wrong getting ticket ID# {ticket_id}")
        response = response.json()
        logs(json.dumps(response, indent=4))

    else:
        ticket = response.json()["ticket"]
        add_json(ticket)

def get_one_ticket_test(ticket_id):
    url = f'https://eastwest.freshservice.com/api/v2/tickets/{ticket_id}'
    key = os.environ["FSKEY"]

    response = requests.get(url, auth=HTTPBasicAuth(key, "X"))

    if response.status_code != 200:
        logs(f"Something went wrong getting ticket ID# {ticket_id}")
        response = response.json()
        logs(json.dumps(response, indent=4))

    else:
        ticket = response.json()["ticket"]
        return ticket
