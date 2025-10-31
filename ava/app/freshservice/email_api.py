import os, requests, json
from requests.auth import HTTPBasicAuth
from app.logs import logs
from app.sql.tickets_db import add_time_last_ai_message_post, update_ai_email, query_ticket
from app.sql.requesters_db import query_requester

def post_email(ticket, ai_response):
    ticket_id = ticket.get("id")
    email = ai_response.get("ai_email")

    check = is_vip(json.loads(ticket.get("json")))

    if check is True:
        ai_response["attempts"] = 10
        logs(f"Not posting AI email to ticket ID# {ticket_id} since requester is VIP")
        update_ai_email(ticket_id, ai_response)
        return


    url = f"https://eastwest.freshservice.com/api/v2/tickets/{ticket_id}/reply"
    key = os.environ["FSKEY"]

    header = {
            "Content-Type": "application/json"
            }
    payload = {
            "body": email 
            }

    response = requests.post(json=payload, headers=header, url=url, auth=HTTPBasicAuth(key, "x"))

    if response.status_code == 201:
        ai_response["attempts"] = 0
        logs(f"Successfully posted AI email to ticket ID# {ticket_id}")
        add_time_last_ai_message_post(ticket_id)
        update_ai_email(ticket_id, ai_response)

    else:
        logs(f"Failed to post AI email to ticket ID# {ticket_id}")
        attempts = ai_response["attempts"]

        if attempts is None:
            ai_response["attempts"] = 1
            update_ai_email(ticket_id, ai_response)

        else:
            ai_response["attempts"] += 1
            update_ai_email(ticket_id, ai_response)


def is_vip(ticket: dict) -> bool:
    requester_id = ticket.get("requester_id")

    requester = query_requester(requester_id)

    return requester.get("vip")
