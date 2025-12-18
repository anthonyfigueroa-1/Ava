import requests, os

from requests.auth import HTTPBasicAuth

from app.logs import logs
from app.sql.tickets import add_resolution_note

key = os.environ["AVA"]

def put_resolution_note(ticket, resolution_note):
    id = ticket.get("id")
    url = f"https://eastwest.freshservice.com/api/v2/tickets/{id}"

    header = {
            "Content-Type": "application/json"
            }

    input = {
            "resolution_notes": resolution_note
            }

    put_retries = ticket.get("resolution_note_put")
    if put_retries is None:
        put_retries = 0

    retries = 0

    while True:
        try:
            response = requests.put(url=url, headers=header, json=input, auth=HTTPBasicAuth(key, 'x'), timeout=(20,20))

            if response.status_code != 200:
                retries += 1
                logs(f"Failed to post resolution_note for ticket ID# {id} with code of {response.status_code}")
            else:
                logs(f"Successfully posted resolution_note for ticket ID# {id}")
                break 

        except requests.Timeout:
            retries += 1
            logs(f"Timout error posting resolution_note for ticket ID# {id}")

        
        if retries > 2:
            logs(f"Tried to PUT resolution note for ticket ID# {id} 3 consecutive times and failed, will stop attempting requst.")
            put_retries += 1
            break

    add_resolution_note(ticket, resolution_note, put_retries)
