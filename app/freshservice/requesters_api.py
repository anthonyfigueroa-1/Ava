import os, requests, json
from requests.auth import HTTPBasicAuth
from requests.models import ReadTimeoutError
from app.logs import logs
from app.sql.requesters_db import add_requesters_table

def get_requester(requester_id):
    if requester_id:
        key = os.environ["FSKEY"]

        retries = 0
        while True:
            try:
                url = f"https://eastwest.freshservice.com/api/v2/requesters/{requester_id}"
                response = requests.get(url, auth=HTTPBasicAuth(key, "X"), timeout=(5, 20))

                if response.status_code == 200:
                    requester = response.json()["requester"]
                    
                    add_requesters_table(requester)
                    break

                else:
                    data = response.json()
                    logs(f"Something went wrong when getting requester for ticket ID# {ticket.get("id")}")
                    logs(f"Status code: {response.status_code}")
                    logs(json.dumps(data, indent=4))
             
            except requests.exceptions.ReadTimeout:
                if retries < 5:
                    retries += 1
                else:
                    break

