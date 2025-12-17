import requests, os

from requests.auth import HTTPBasicAuth

from app.logs import logs
from app.sql.tickets import add_resolution_note

key = os.environ["AVA"]

def put_resolution_note(ticket, resolution_note):
    id = ticket.get("id")
    url = f"https://eastwest.freshservice.com/api/v2/tickets/{id}?include=assets"

    header = {
            "Content-Type": "application/json"
            }

    input = {
            "resolution_notes_html": resolution_note
            }

    retries = 0

    while True:
        try:
            response = requests.put(url=url, headers=header, json=input, auth=HTTPBasicAuth(key, 'x'), timeout=(20,20))

            if response:
                if response.status_code != 201:
                    logs(f"Failed to post resolution_note for ticket ID# {id} with code of {response.status_code}")
                else:
                    add_resolution_note(ticket, resolution_note)
                    break 

        except requests.Timeout:
            if retries > 2:
                logs(f"Timout error posting resolution_note happend 3 times consecutavily for ticket ID# {id}, will ignore posting resolution_note")
                break
            else:
                retries += 1
                logs(f"Timout error posting resolution_note for ticket ID# {id}")
