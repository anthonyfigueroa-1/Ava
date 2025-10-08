from app.sql.tickets_db import query_ticket_class
from app.classes.ticket import Ticket
from app.logs import logs
import time

def filter_initial_tickets(tickets):
    filtered_tickets = []
    
    logs("Querying tickets in tickets database for filtering")
    for ticket in tickets:
        id = ticket.get("id")
        ticket_class =  query_ticket_class(id)
        time = ticket_class.time_last_ai_message_post
        attempts = ticket_class.ai_attempts
        recieved = ticket_class.ticket_created
        
        #Math to find out if enough time has passed to send message
        now = time.time()
        time_dif = now - recieved
        #10 minutes in seconds
        tenmin = 60 * 10

        if time is None and attempts > 0 and attempts <= 5 and time_dif > tenmin:
            filtered_tickets.append(ticket)

    return filtered_tickets

def filter_initial_ticket_test(ticket):
    id = ticket.get("id")
    logs("Querying ticket for filtering")
    ticket_class =  query_ticket_class(id)
    time_message_post = ticket_class.time_last_ai_message_post
    attempts = ticket_class.ai_attempts
    recieved = ticket_class.ticket_created

    #Math to find out if enough time has passed to send message
    now = int(time.time())
    time_dif = now - recieved
    #10 minutes in seconds
    tenmin = 60 * 10

    if time_message_post is None and attempts > 0 and attempts <= 5 and time_dif > tenmin:
        return ticket
    else:
        return None
