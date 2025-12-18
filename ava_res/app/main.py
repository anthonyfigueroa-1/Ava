from app.freshservice.conversations import get_ticket_conversations
from app.sql.tickets import query_closed_tickets, update_ticket_table, query_one_ticket
from app.freshservice.tickets import get_one_ticket
from app.ai.resolution_note import ai_resolution_note
from app.argparse import parse_args
from app.logs import logs

import time, sys

def main() -> None:
    args = parse_args()

    arg_id = args.id if args.id else None

    while True:
        if arg_id:
            ticket = query_one_ticket(arg_id)
            if ticket:
                logs(f"Starting test run on ticket ID# {arg_id}")
                tickets = [ticket]
            else:
                logs(f"Could not run test on ticket ID# {arg_id}! Could not find in DB")
                sys.exit(1) 
        else:
            tickets = query_closed_tickets()

        if not tickets:
            logs("All tickets have either been updating or do not require updating at this time.")
            logs("Sleeping for 5 minutes")

            #5 Minutes
            time.sleep(300)

        for ticket in tickets:
            if arg_id:
                id = ticket.get("id")
            else:
                id = ticket[0]

            ticket = get_one_ticket(id)
            ai_resolution_note(ticket)

            if arg_id:
                logs(f"Ending test run on ticket ID# {id}")
                sys.exit(0)
            else:
                time.sleep(1)

def runner() -> None:
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting...")
