from app.sql.tickets_db import query_ticket, update_ai_attempts
from app.logs import logs
import time, json, zoneinfo
from datetime import time as dtime
from datetime import datetime

def filter_initial_tickets(tickets):
    filtered_tickets = []
    
    logs("Querying tickets for AI response filtering")
    for ticket in tickets:
        id = ticket.get("id")
        ticket_class = query_ticket(id)

        mtn_zone = zoneinfo.ZoneInfo("America/Denver")
        now_mtn = datetime.now(tz=mtn_zone)

        work_start = dtime(7, 30, 0)
        work_end = dtime(18, 30, 0)

        attempts = ticket_class.get("ai_attempts")
        ticket_created = ticket_class.get("ticket_created")

        if (attempts is None or (attempts > 0 and attempts <= 5)):

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
                ticket_created = ticketdb.get("ticket_created")
                tenmin = 60*10
                diff = int(now_unix)-int(ticket_created)

                if diff >= tenmin:
                    filtered_tickets.append(ticket) 

                else:
                    update_ai_attempts(id, 15) #15 is code for on-call, to avoid posting empty field in FS

    return filtered_tickets

def filter_post_to_fs(tickets):
    filtered_tickets = []

    logs("Querying tickets for posting AI response to FS filtering")
    for ticket in tickets:
        id = ticket.get("id")
        ticketdb = query_ticket(id)

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
                    and (ai_attempts != 15) #15 is code for on-call
                    ):

                       filtered_tickets.append(ticket) 

        except json.decoder.JSONDecodeError:
            logs("Cannot work on ticket because either [ai_email, ai_note, ai_next_steps] is not a JSON in the database")
            continue

    return filtered_tickets

def filter_ai_response_test(ticket):
    id = ticket.get("id")
    logs("Querying ticket for AI response filtering")
    ticket =  query_ticket(id)
    time_message_post = ticket.get("time_last_ai_message_post")
    attempts = ticket.get("ai_attempts")
    recieved = ticket.get("ticket_created")

    #Math to find out if enough time has passed to send message
    now = int(time.time())
    time_dif = now - recieved
    #10 minutes in seconds
    tenmin = 60 * 10

    #Removing 10 minute wait per Ryan's request.
    if (attempts is None or (attempts > 0 and attempts <= 5)):
        return ticket
    else:
        return None

def filter_post_to_fs_test(ticket):
    id = ticket.get("id")
    logs("Querying ticket for posting AI response to FS filtering")
    ticket = query_ticket(id)

    post_note = ticket.get("post_note")
    post_email = ticket.get("post_email")
    put_fields = ticket.get("put_fields")
    ai_attempts = ticket.get("ai_attempts")

    if ((post_note is None or (post_note > 0 and post_note <=3)) or (put_fields is None or (put_fields > 0 and put_fields <=3))) and (ai_attempts == 0):
        return ticket
    else:
        return None
