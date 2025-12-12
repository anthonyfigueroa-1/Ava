import os, requests, json, re
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
            "ai_email": f"*Email: {ai_response.get("ai_email")}",
            "ai_note": f"{ai_response.get("ai_note")}",
            "ai_next_steps": f"*Next steps: {ai_response.get("ai_next_steps")}"
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

        ai_note = (diff[key])

#        ai_note = re.sub(r"[\\n]+", "<br>", ai_note)

        header = {
                "Content-Type": "application/json"
                }

        payload = {
                "body": ai_note
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

    except requests.exceptions.ReadTimeout or requests.exceptions.ConnectTimeout:
        logs(f"Timeout Error for posting private note for ticket ID# {ticket_id}")
        pass

def check_if_null(ai_response, key):
    message = ai_response.get(f"{key}")
    
    if not message:
        return False

def misc_private_note(ticket_id, note):
    url = f"https://eastwest.freshservice.com/api/v2/tickets/{ticket_id}/notes"
    fskey = os.environ["FSKEY"]

    header = {
            "Content-Type": "application/json"
            }

    payload = {
            "body": note
            }

    response = requests.post(url=url, json=payload, headers=header, auth=HTTPBasicAuth(fskey, 'X'), timeout=(20,20))

    if response.status_code != 201:
        logs(f"Failed to post misc note to ticket ID# {ticket_id} with status code of {response.status_code}")

    else:
        logs(f"Successfully posted note letting other agents know Ava is working on this ticket")
        note = response.json()["conversation"]
        note_id = note.get("id")
        return note_id

def delete_private_note(note_id):
    url = f"https://eastwest.freshservice.com/api/v2/conversations/{note_id}"
    fskey = os.environ["FSKEY"]

    response = requests.delete(url=url, auth=HTTPBasicAuth(fskey, "X"), timeout=(20,20))

    if response.status_code != 204:
        logs(f"Failed to delete note ID {note_id}, with status code of {response.status_code}")

    else:
        logs(f"Successfully deleted note ID {note_id}")
