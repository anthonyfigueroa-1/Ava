import os, requests
from requests.auth import HTTPBasicAuth
from app.sql.requesters_db import add_requesters_table

def get_requester(ticket):
    requester_id = ticket.get("requester_id")

    if requester_id:
        key = os.environ["FSKEY"]

        url = f"https://eastwest.freshservice.com/api/v2/requesters/{requester_id}"
        response = requests.get(url, auth=HTTPBasicAuth(key, "X"))
    
        if response.status_code == 200:
            requester = response.json()["requester"]
            
            add_requesters_table(requester)
