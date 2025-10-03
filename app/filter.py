from app.sql.tickets_db import query_ai_response
def filter_tickets(tickets):
    filtered_tickets = []
    
    for ticket in tickets:
        id = ticket.get("id")
        ai_response = query_ai_response(id)
        responses = True
        #Checks values of the tuple that was grabbed from the tickets DB and the program will check if there is an entry for first_response and for private_note. If one does not exist, it will be appended to filtered tickets.
        if ai_response:
            if ai_response[0] is None or ai_response[1] is None:
                responses = False
        #Cannot process ai_response if both are of None type so doing this to check otherwise.
        if ai_response is None:
            responses = False

        if responses == False:
            filtered_tickets.append(ticket)

    return filtered_tickets
