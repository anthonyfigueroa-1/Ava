from app.sql.tickets_db import query_ticket, update_ai_attempts
from app.logs import logs
import time, json, zoneinfo
from datetime import time as dtime
from datetime import datetime

def filter_initial_tickets(tickets):
    #need to remove this
    filtered_tickets = []
    
    logs("Querying tickets for AI response filtering")
    #will get rid of loop
    for ticket in tickets:
        id = ticket.get("id")
        ticket_class = query_ticket(id)

        mtn_zone = zoneinfo.ZoneInfo("America/Denver")
        now_mtn = datetime.now(tz=mtn_zone)

        work_start = dtime(7, 30, 0)
        work_end = dtime(18, 30, 0)

        attempts = ticket_class.get("ai_attempts")
        ticket_created = ticket_class.get("ticket_created")

        requester_id = ticket.get("requester_id")
        tech_global = 5000163334

        if (attempts is None or attempts == 15 or (attempts >= 1 and attempts <= 5)):

            if requester_id == tech_global:
                update_ai_attempts(id, 20) #20 is code for TECH GLOBAL requester
                continue

            """If/else statement below is to assist with script getting in the way of on-call by waiting 10 min.
            before posting the messages and status to the ticket. This will allow on-call person to still be
            called but for the script to still post the AI message to the ticket."""
            if (
                    (now_mtn.time() > work_start
                    and now_mtn.time() < work_end)
                    and (now_mtn.weekday() <= 4)
                    ):
                filtered_tickets.append(ticket)
                
            else:
                now_unix = time.time()
                ticket_created = ticket_class.get("ticket_created")
                tenmin = 60*10
                diff = int(now_unix)-int(ticket_created)

                if diff >= tenmin:
                    filtered_tickets.append(ticket) 

                else:
                    update_ai_attempts(id, 15) #15 is code for on-call, to avoid posting empty field in FS

    #filtered_ai_ticket(ticket)
    #will return bool
    return filtered_tickets

def filtered_ai_ticket(ticket):

    if filter_ai_response:
        logs(f"Will now start working on generating AI responses for tickets that passed filter.")
        for ticket in filter_ai_response:
            id = ticket.get("id")

            get_conversations(id)
            add_requesters(tickets)

            logs(f"Working on generating AI responses for ticket ID# {id}")

            ticket = query_ticket(id)
            
            #Skips over ticket if no in list. Should have been in list from prior loop. So something went wrong if that's the case.
            if not ticket:
                logs(f"Could not find ticket ID# {id} in database, skipping over it")
                continue

            #first_response() returns a tuple... it returns the email for the user and the private note for the ticket, for the agent.
            responses = first_response(ticket, instructions)

        logs("End ai_response filter run.")

    else:
        logs("No tickets need AI generation right now")

def filter_post_to_fs(tickets):
    filtered_tickets = []

    logs("Querying tickets for posting AI response to FS filtering")
    for ticket in tickets:
        id = ticket.get("id")
        ticketdb = query_ticket(id)

        ai_attempts = ticketdb.get("ai_attempts")

        if ai_attempts not in (15, 20, 25):
            #15 is on-call ticket wait
            #20 is TECH GLOBAL tickets
            #25 is any manual tickets I marked on DB as not needing attention

            try:

                email = (json.loads(ticketdb.get("ai_email"))).get("attempts")
                note = (json.loads(ticketdb.get("ai_note"))).get("attempts")
                ns = (json.loads(ticketdb.get("ai_next_steps"))).get("attempts")
                put_fields = ticketdb.get("put_fields")
                ai_attempts = ticketdb.get("ai_attempts")

                if (
                        ((note is None or (note > 0 and note <=3)) 
                        or (email is None or (email > 0 and email <=3)) 
                        or (ns is None or (ns > 0 and ns <= 3))
                        or (put_fields is None or (put_fields > 0 and put_fields <=3)))
                        ):

                           filtered_tickets.append(ticket) 

            except json.decoder.JSONDecodeError or TypeError:
                logs("Cannot work on ticket because either [ai_email, ai_note, ai_next_steps] is not a JSON or is None in the database")
                continue

    return filtered_tickets
