from app.freshservice.conversations import get_ticket_conversations
from app.sql.tickets import query_open_tickets, update_ticket_table
from app.freshservice.tickets import get_one_ticket
from app.logs import logs

import time

def main() -> None:
    while True:

        tickets = query_open_tickets()

        if not tickets:
            logs("All tickets have either been updating or do not require updating at this time.")
            logs("Sleeping for 5 minutes")

            #5 Minutes
            time.sleep(300)

        for ticket in tickets:
            id = ticket[0]

            ticket = get_one_ticket(id)
            
            if not ticket:
                continue

            conversation = get_ticket_conversations(ticket)

            update_ticket_table(ticket, conversation)
            
            time.sleep(1)

def runner() -> None:
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting...")
