from app.freshservice.tickets_api import get_tickets, get_one_ticket
from app.freshservice.departments_api import get_departments
from app.freshservice.requesters_api import get_requester
from app.freshservice.email_api import post_email
from app.freshservice.private_note_api import post_private_note
from app.freshservice.conversations_api import get_conversations
from app.sql.create_db import create_db
from app.sql.tickets_db import create_tickets_table, add_tickets_table, add_ai_response, query_ticket
from app.sql.departments_db import create_departments_table, query_departments_table
from app.sql.requesters_db import create_requesters_table
from app.ai.responses import first_response
from app.logs import logs
from app.filter import filter_tickets
from app.arg_parse import parse_args

import sys

def main():
    #functions to create the database and the tables for the databases
    create_db()
    create_tickets_table()
    create_departments_table()
    create_requesters_table()
    logs("All tables were either created or already existed in database.")

    #Create arg parse to test individual tickets. 
    args = parse_args()
    arg_id = args.id if args.id else None

    #Used for test runs
    if arg_id:
        logs("Running test run")
        ticket = query_ticket(arg_id)
        if not ticket:
            ticket = get_one_ticket(arg_id)
            get_requester(ticket)
            add_tickets_table(ticket)
            ticket = query_ticket(arg_id)

        get_conversations(arg_id)
        responses = first_response(ticket)
        add_ai_response(responses, arg_id)
        post_email(arg_id, responses)
        get_conversations(arg_id)
        #Don't have access to post private notes via api's right now
        #post_private_note(arg_id, responses)
        sys.exit(0)
    #^^^Used for test runs^^^


    #Request functions for GET API's from Freshservice
    tickets = get_tickets()

    #Will work on only having this run every X time the script loops.
    #get_departments()

    #Filters tickets based on if they exist and if there is values for AI first_response and private_note fields.
    logs("Filtering through batch of tickets.")

    #Filter tickets based off of time_last_message_sent field in the tickets table of the database. If empty, then ticket will added to first_response_tickets.
    first_response_tickets = filter_tickets(tickets)

    if first_response_tickets:
        for ticket in first_response_tickets:
            id = ticket.get("id")
            logs(f"Working on ticket ID# {id}")

            #Will grab the requester info from the ticket and put some of that data from FS and store that in the requesters table in the database.
            get_requester(ticket)
            add_tickets_table(ticket)

            #first_response() returns a tuple... it returns the email for the user and the private note for the ticket, for the agent.
            responses = first_response(ticket)

            #Stores response of ai tuple response to the tickets table of the db.
            add_ai_response(responses, id)

            #Sends email response to user of the ticket
            post_email(id, responses)

            #Updates itself on all the conversations that happened, up to this point, on the ticket, using FS API's. Stores this info on tickets table of the db.
            get_conversations(id)
            
            #Don't have access to post private notes via api's right now
            #post_private_note(id, responses)

def runner():
    #Just starts the script and ends without dumping an error when exiting using Ctrl+c.
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting script")
