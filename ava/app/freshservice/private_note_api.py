import os, requests, json
from requests.auth import HTTPBasicAuth
from app.logs import logs
from app.sql.tickets_db import update_ai_email, update_ai_note, update_ai_next_steps

dispatch = {
        "ai_email": update_ai_email,
        "ai_note": update_ai_note,
        "ai_next_steps": update_ai_next_steps
        }

def post_private_note(ticket_id, ai_response):
    diff = {
            "ai_email": f"<br>Email: {ai_response.get("ai_email")}",
            "ai_note": f"<br>Note: {ai_response.get("ai_note")}",
            "ai_next_steps": f"<br>Next steps: {ai_response.get("ai_next_steps")}"
            }

    key = next((ai_type for ai_type in ai_response if ai_type in dispatch), None)

    check = check_if_null(ai_response, key)
    
    if not key or check is False:
        ai_response["attempts"] = 5
        dispatch[key](ticket_id, ai_response)
        return

    try:
        url = f"https://eastwest.freshservice.com/api/v2/tickets/{ticket_id}/notes"
        fskey = os.environ["FSKEY"]

        header = {
                "Content-Type": "application/json"
                }

        payload = {
                "body": f"USING THIS NOTE FOR AI TESTING<br><br>{diff[key]}"
                }

        response = requests.post(url=url, json=payload, headers=header, auth=HTTPBasicAuth(fskey, 'X'), timeout=(20,20))


        if response.status_code == 201:
            ai_response["attempts"] = 0
            logs(f"Successfully posted {key} as a private note to ticket ID# {ticket_id}")
            dispatch[key](ticket_id, ai_response)

        else:
            logs(f"Failed to post AI note to ticket ID# {ticket_id} with status code of {response.status_code}")
            error = response.json()
            logs(json.dumps(error, indent=4))

            if ai_response.get("attempts") is None:
                ai_response["attempts"] = 1
                dispatch[key](ticket_id, ai_response)

            else:
                ai_response["attempts"] += 1
                dispatch[key](ticket_id, ai_response)

    except requests.exceptions.ReadTimeout:
        logs(f"Timeout Error for posting private note for ticket ID# {ticket_id}")
        pass
    except requests.exceptions.ConnectTimeout:
        logs(f"Timeout Error for posting private note for ticket ID# {ticket_id}")
        pass

def check_if_null(ai_response, key):
    message = ai_response.get(f"{key}")
    
    if not message or 'NO AI NEEDED' in message:
        return False
