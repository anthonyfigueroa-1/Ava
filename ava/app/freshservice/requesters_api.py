import os, requests, time
from requests.auth import HTTPBasicAuth
from app.logs import logs
from app.sql.requesters_db import add_requesters_table

def get_requester(ticket):
    requester_id = ticket.get("requester_id")
    ticket_id = ticket.get("id")

    counter = 0

    while True:
        if counter > 3:
            break

        if requester_id:
            key = os.environ["FSKEY"]

            try:
                url = f"https://eastwest.freshservice.com/api/v2/requesters/{requester_id}"
                response = requests.get(url, auth=HTTPBasicAuth(key, "X"), timeout=(5, 20))

                if response.status_code == 404:
                    logs(f"Something went wrong when getting requester ID# {requester_id} for ticket ID# {ticket_id}")
                    logs(f"Status code: {response.status_code}")
                    break

                if response.status_code != 200:
                    logs(f"Something went wrong when getting requester ID# {requester_id} for ticket ID# {ticket_id}")
                    logs(f"Status code: {response.status_code}")
                    counter += 1
                    time.sleep(3)
                        
                else:
                    requester = response.json()["requester"]
                    add_requesters_table(requester)
                    break
             
            except requests.exceptions.Timeout:
                logs(f"Timeout Error for getting requester ID# {requester_id} for ticket ID# {ticket_id}")
                counter += 1
                time.sleep(5)

def get_requester_by_id(requester_id):
    counter = 0

    while True:
        if counter > 2:
            break

        if requester_id:
            key = os.environ["FSKEY"]

            try:
                url = f"https://eastwest.freshservice.com/api/v2/requesters/{requester_id}"
                response = requests.get(url, auth=HTTPBasicAuth(key, "X"), timeout=(5, 20))

                if response.status_code == 404:
                    logs(f"Something went wrong when getting requester ID# {requester_id}")
                    logs(f"Status code: {response.status_code}")
                    break

                if response.status_code != 200:
                    logs(f"Something went wrong when getting requester ID# {requester_id}")
                    logs(f"Status code: {response.status_code}")
                    counter += 1
                    time.sleep(3)
                        
                else:
                    requester = response.json()["requester"]
                    add_requesters_table(requester)
                    break
             
            except requests.exceptions.Timeout:
                logs(f"Timeout Error for getting requester ID# {requester_id}")
                counter += 1
                time.sleep(5)
