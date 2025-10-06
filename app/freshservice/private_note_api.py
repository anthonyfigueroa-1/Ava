import os, requests
from requests.auth import HTTPBasicAuth

def post_private_note(ticket_id, ai_response):
    url = f"https://eastwest.freshservice.com/api/v2/{ticket_id}/notes"
    key = os.environ["FSKEY"]

    header = {
            "Content-Type": "application/json"
            }

    payload = {
            "body": ai_response[1]
            }

    response = requests.post(url=url, json=payload, headers=header, auth=HTTPBasicAuth(key, 'X'))
