import json

from app.logs import logs
from app.sql.requesters_db import query_requester
from app.freshservice.requesters_api import get_requester_by_id

def convo_user_id_convert(tickets):
    check_convo_for_current_ticket(tickets)

    user_ids = []
    for ticket in tickets:
        if isinstance(ticket, tuple):
            ticket = ticket[0]
        conversations = ticket.get("conversations")
        if conversations:
            for convo in conversations:
                user_id = convo.get("user_id")
                user_ids.append(user_id)
            
    if not user_ids:
        return

    user_ids = list(set(user_ids))
    #Above gets converted to set to get rid of duplicates and back to a list

    users = []
    for user_id in user_ids:
        retries = 0
        while True:
            user = query_requester(user_id)
            if user:
                users.append(user)
                break
            else:
                if retries == 1:
                    break
                get_requester_by_id(user_id)    
                retries+=1

    return users

def check_convo_for_current_ticket(tickets):
    c_ticket = tickets[0]
    c_convo = c_ticket.get("conversations")

    if not c_convo:
        tickets.pop(0)
