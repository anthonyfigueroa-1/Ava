from app.sql.tickets import query_open_tickets
from app.freshservice.tickets import get_one_ticket
from app.check_status import check_status
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
            status = ticket[1]

            ticket = get_one_ticket(id)
            
            if not ticket:
                continue

            check_status(ticket)

            time.sleep(3)

def runner() -> None:
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting...")
