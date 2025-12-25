from datetime import time as dtime
from datetime import datetime
from zoneinfo import ZoneInfo

def filter_new_ticket(ticket):
    id = ticket.get("id")
    ticket_class = query_ticket(id)

    mtn_zone = ZoneInfo("America/Denver")
    now_mtn = datetime.now(tz=mtn_zone)

    work_start = dtime(7, 30, 0)
    work_end = dtime(18, 30, 0)

    attempts = ticket_class.get("ai_attempts")
    ticket_created = ticket_class.get("ticket_created")
    status = ticket_class.get("status")
    responder = ticket_class.get("responder")

    requester_id = ticket.get("requester_id")
    tech_global = 5000163334

    if (attempts is None or attempts == 15 or (attempts >= 1 and attempts <= 5)):
        if requester_id == tech_global:
            update_ai_attempts(id, 20) #20 is code for TECH GLOBAL requester
            return
        elif responder:
            update_ai_attempts(id, 22) 
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

