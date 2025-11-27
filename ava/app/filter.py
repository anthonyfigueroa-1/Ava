from app.freshservice.email_api import post_email
from app.freshservice.fields_api import put_fields
from app.freshservice.private_note_api import post_private_note
from app.freshservice.service_request_api import get_service_request_info
from app.sql.tickets_db import query_ticket, update_ai_attempts, add_requester
from app.freshservice.conversations_api import get_conversations
from app.ai.responses import first_response
from app.logs import logs

import time, json, zoneinfo
from datetime import time as dtime
from datetime import datetime

from app.ticket_type import check_if_service_request

#15 is on-call ticket wait
#20 is TECH GLOBAL tickets
#21 is Resolved/Closed tickets
#22 is ticket already assigned to an agent
#25 is any manual tickets I marked on DB as not needing attention

def filter_initial_tickets(ticket):
    id = ticket.get("id")
    ticket_class = query_ticket(id)

    mtn_zone = zoneinfo.ZoneInfo("America/Denver")
    now_mtn = datetime.now(tz=mtn_zone)

    work_start = dtime(7, 30, 0)
    work_end = dtime(18, 30, 0)

    attempts = ticket_class.get("ai_attempts")
    ticket_created = ticket_class.get("ticket_created")
    status = ticket_class.get("status")
#    responder_id = ticket_class.get("responder_id")

    requester_id = ticket.get("requester_id")
    tech_global = 5000163334

    if (attempts is None or attempts == 15 or (attempts >= 1 and attempts <= 5)):
        if requester_id == tech_global:
            update_ai_attempts(id, 20) #20 is code for TECH GLOBAL requester
            return
#        elif responder_id:
#            update_ai_attempts(id, 22) 
        elif status in (4, 5):
            update_ai_attempts(id, 21)
            return

        """If/else statement below is to assist with script getting in the way of on-call by waiting 10 min.
        before posting the messages and status to the ticket. This will allow on-call person to still be
        called but for the script to still post the AI message to the ticket."""
        if (
                (now_mtn.time() > work_start
                and now_mtn.time() < work_end)
                and (now_mtn.weekday() <= 4)
                ):
            filtered_ai_ticket(ticket)
            return True
            
        else:
            now_unix = time.time()
            ticket_created = ticket_class.get("ticket_created")
            tenmin = 60*10
            diff = int(now_unix)-int(ticket_created)

            if diff >= tenmin:
                filtered_ai_ticket(ticket)
                return True

            else:
                update_ai_attempts(id, 15) #15 is code for on-call, to avoid posting empty field in FS

def filtered_ai_ticket(ticket):
    id = ticket.get("id")

    add_requester(ticket)
    get_conversations(id)
    check_if_service_request(ticket)

    logs(f"Working on generating AI responses for ticket ID# {id}")

    ticket = query_ticket(id)
    
    #Skips over ticket if not in list. Should have been in list from prior loop. So something went wrong if that's the case.
    if not ticket:
        logs(f"Could not find ticket ID# {id} in database, skipping over it")
        return

    first_response(ticket)

def filter_post_to_fs(ticket):
    id = ticket.get("id")
    ticketdb = query_ticket(id)

    ai_attempts = ticketdb.get("ai_attempts")

    if ai_attempts not in (15, 20, 21, 22, 25):
        
        email = ticketdb.get("ai_email").get("attempts")
        note = ticketdb.get("ai_note").get("attempts")
        ns = ticketdb.get("ai_next_steps").get("attempts")
        put_fields = ticketdb.get("put_fields")
        ai_attempts = ticketdb.get("ai_attempts")

        if (
                ((note is None or (note > 0 and note <=3)) 
                or (email is None or (email > 0 and email <=3)) 
                or (ns is None or (ns > 0 and ns <= 3))
                or (put_fields is None or (put_fields > 0 and put_fields <=3)))
                ):

                   filtered_post_ticket(ticket) 
                   return True

def filtered_post_ticket(ticket):
    id = ticket.get("id")

    logs(f"Working on updating ticket ID# {id} in FreshService.")

    ticket = query_ticket(id)

    field_put = ticket.get("put_fields")
    ai_email = ticket.get('ai_email')
    ai_note = ticket.get('ai_note')
    ai_next_steps = ticket.get('ai_next_steps')

    email_attempts = ai_email.get('attempts')
    note_attempts = ai_note.get('attempts')
    next_steps_attempts = ai_next_steps.get('attempts')

    if email_attempts is None or (email_attempts > 0 and email_attempts <= 3):
        post_email(ticket, ai_email)
    
    if note_attempts is None or (note_attempts > 0 and note_attempts <= 3):
        post_private_note(id, ai_note)

    if next_steps_attempts is None or (next_steps_attempts > 0 and next_steps_attempts <= 3):
        post_private_note(id, ai_next_steps)

    if field_put is None or (field_put > 0 and field_put <= 3):
        put_fields(id) 
