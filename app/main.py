from app.freshservice.tickets_api import get_tickets
from app.freshservice.departments_api import get_departments
from app.freshservice.requesters_api import get_requester
from app.sql.create_db import create_db
from app.sql.tickets_db import create_tickets_table, add_tickets_table, add_ai_response
from app.sql.departments_db import create_departments_table, query_departments_table
from app.sql.requesters_db import create_requesters_table
from app.ai.responses import first_response
from app.logs import logs
from app.filter import filter_tickets

def main():
    #functions to create the database and the tables for the databases
    create_db()
    create_tickets_table()
    create_departments_table()
    create_requesters_table()
    logs("All tables were either created or already existed in database.")

    #Request functions for GET API's from Freshservice
    tickets = get_tickets()

    #Will work on only having this run every X time the script loops.
    #get_departments()

    #Filters tickets based on if they exist and if there is values for AI first_response and private_note fields.
    logs("Filtering through tickets")
    filtered_tickets = filter_tickets(tickets)

    if filtered_tickets:
        logs("OpenAI will now start working on filtered tickets")
        for ticket in filtered_tickets:
            id = ticket.get("id")
            logs(f"Working on ticket ID# {id}")

            get_requester(ticket)
            add_tickets_table(ticket)
            logs(f"OpenAI is generating a response and private note for ticket ID# {id}")
            responses = first_response(ticket)
            add_ai_response(responses, id)

def runner():
    #Just starts the script and ends without dumping an error when exiting using Ctrl+c.
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting script")
