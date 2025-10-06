import os, requests
from requests.auth import HTTPBasicAuth
from app.logs import logs

def post_email(ticket_id, ai_response):
    url = f"https://eastwest.freshservice.com/api/v2/tickets/{ticket_id}/reply"
    key = os.environ["FSKEY"]

    header = {
            "Content-Type": "application/json"
            }
    payload = {
            "body": ai_response[0]
            }

    response = requests.post(json=payload, headers=header, url=url, auth=HTTPBasicAuth(key, "x"))

    if response.status_code in (200, 406):
        logs(f"Successfully posted AI email to ticket ID# {ticket_id}")
