from app.sql.tickets_db import query_ticket_class, query_ticket
from app.classes.ticket import Ticket
from app.logs import logs
import time

def filter_initial_tickets(tickets):
    filtered_tickets = []
    
    logs("Querying ticket for AI response filtering")
    for ticket in tickets:
        id = ticket.get("id")
        ticket_class = query_ticket(id)

        time_message_post = ticket_class.get("time_last_ai_message_post")
        attempts = ticket_class.get("ai_attempts")
        recieved = ticket_class.get("ticket_created")

        #Math to find out if enough time has passed to send message
        now = int(time.time())
        time_dif = now - recieved
        #10 minutes in seconds
        tenmin = 60 * 10

        #Removing 10 minute wait per Ryan's request.
        if (attempts is None or (attempts > 0 and attempts <= 5)):
            filtered_tickets.append(ticket)

    return filtered_tickets

def filter_post_to_fs(tickets):
    filtered_tickets = []

    logs("Querying ticket for posting AI response to FS filtering")
    for ticket in tickets:
        id = ticket.get("id")
        ticket_class = query_ticket(id)

        post_note = ticket_class.get("post_note")
        post_email = ticket_class.get("post_email")
        put_fields = ticket_class.get("put_fields")
        ai_attempts = ticket_class.get("ai_attempts")

        #removed from filter below for testing((post_email is None or (post_email > 0 and post_email <= 3)) or 
        if ((post_note is None or (post_note > 0 and post_note <=3)) or (put_fields is None or (put_fields > 0 and put_fields <=3))) and (ai_attempts == 0):
            filtered_tickets.append(ticket)

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

    if ((post_email is None or (post_email > 0 and post_email <= 3)) or (post_note is None or (post_note > 0 and post_note <=3)) or (put_fields is None or (put_fields > 0 and put_fields <=3))) and (ai_attempts == 0):
        return ticket
    else:
        return None
