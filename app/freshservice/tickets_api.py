import requests, os
from requests.auth import HTTPBasicAuth
from app.logs import logs

def get_tickets():
    url = "https://eastwest.freshservice.com/api/v2/tickets"
    key = os.environ["FSKEY"]

    response = requests.get(url, auth=HTTPBasicAuth(key, "X"))
    tickets = response.json()["tickets"]

    if response.status_code == 200:
        logs("Got batch of tickets")

    return tickets

def get_one_ticket(ticket_id):
    url = f"https://eastwest.freshservice.com/api/v2/tickets/{ticket_id}"
    key = os.environ["FSKEY"]

    response = requests.get(url, auth=HTTPBasicAuth(key, "X"))
    ticket = response.json()["ticket"]

    if response.status_code == 200:
        logs(f"Got ticket ID# {ticket_id}")

    return ticket
