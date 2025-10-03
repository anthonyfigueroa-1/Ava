import requests, os
from requests.auth import HTTPBasicAuth

def get_tickets():
    url = "https://eastwest.freshservice.com/api/v2/tickets"
    key = os.environ["FSKEY"]

    response = requests.get(url, auth=HTTPBasicAuth(key, "X"))
    tickets = response.json()["tickets"]

    return tickets
