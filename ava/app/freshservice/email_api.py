import os, requests, json
from requests.auth import HTTPBasicAuth
from app.logs import logs
from app.sql.tickets_db import add_time_last_ai_message_post, update_ai_email, query_ticket
from app.sql.requesters_db import query_requester

def post_email(ticket, ai_response):
    ticket_id = ticket.get("id")
    email = ai_response.get("ai_email")

    check = is_vip(ticket.get("json"))
    is_null = check_if_null(email)

    if check is True or is_null is True:
        ai_response["attempts"] = 10
        logs(f"Not posting AI email to ticket ID# {ticket_id}")
        logs(f"VIP: {check}")
        logs(f"NULL: {is_null}")
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

    try:
        response = requests.post(json=payload, headers=header, url=url, auth=HTTPBasicAuth(key, "x"), timeout=(20,20))

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

    except requests.exceptions.ReadTimeout or requests.exceptions.ConnectTimeout:
        logs(f"Timeout error when posting email to ticket ID# {ticket_id}")


def is_vip(ticket: dict) -> bool:
    requester_id = ticket.get("requester_id")

    requester = query_requester(requester_id)

    if requester:
        return requester.get("vip")
    else:
        return False

def check_if_null(email):
    if not email or 'NO AI NEEDED' in email:
        return True 
    else:
        return False
