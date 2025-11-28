import os, json, requests

from requests.auth import HTTPBasicAuth
from requests import get

from app.logs import logs
from app.sql.tickets_db import add_service_request

key = os.environ["FSKEY"]

def get_onboarding_form(ticket: dict) -> None:
    id = ticket.get("id")

    url = f"https://eastwest.freshservice.com/api/v2/tickets/{id}?include=onboarding_context"

    try:
        response = get(url, auth=HTTPBasicAuth(key, 'X'), timeout=(20,20))

        if response != 200:
            logs(f"Failed to get onboarding form for ticket ID# {id} with code of {response.status_code}")
        else:
            response = response.json()["ticket"]
            onboarding_form = response.get("onboarding_context")
            add_service_request(onboarding_form, id)

    except requests.Timeout:
        logs(f"Failed to get onboarding form for ticket ID# {id} due to request timeout")
