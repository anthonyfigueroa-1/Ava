from app.freshservice.tickets_api import get_tickets, get_one_ticket
from app.freshservice.departments_api import get_departments
from app.freshservice.requesters_api import get_requester
from app.freshservice.email_api import post_email
from app.freshservice.private_note_api import post_private_note
from app.freshservice.conversations_api import get_conversations
from app.freshservice.fields_api import put_fields
from app.sql.create_db import create_db
from app.sql.tickets_db import create_tickets_table, add_tickets_table, add_ai_response, query_ticket, query_ticket_class
from app.sql.departments_db import create_departments_table, query_departments_table
from app.sql.requesters_db import create_requesters_table
from app.ai.responses import first_response
from app.logs import logs 
from app.regex import seperate_responses
from app.filter import filter_initial_tickets, filter_ai_response_test, filter_post_to_fs, filter_post_to_fs_test
from app.arg_parse import parse_args
from app.classes.ticket import Ticket

import sys, time, json

def main():
    #functions to create the database and the tables for the databases
    create_db()
    create_tickets_table()
    create_departments_table()
    create_requesters_table()
    logs("All tables were either successfully created or already existed in database.")

    #Create arg parse to test individual tickets. 
    args = parse_args()
    arg_id = args.id if args.id else None

    #<<<Used for test runs>>>
    if arg_id:
        logs("Running test run")

        ticket = get_one_ticket(arg_id)
        add_tickets_table(ticket)

        get_conversations(arg_id)

        filter_ai_response = filter_ai_response_test(ticket)
        if filter_ai_response:
            logs(f"Ticket ID# {arg_id} passed generate ai response filter")

            #moving query_ticket() to ai_response

            responses = first_response(ticket)

        else:
            logs(f"Ticket ID# {arg_id} failed to pass ai response filter")
            logs("End ai_response filter run.")

        filter_post_fs = filter_post_to_fs_test(ticket)

        if filter_post_fs:
            logs(f"Ticket ID# {arg_id} passed post to FS filter")

            ticket = query_ticket(arg_id)

            responses = json.loads(ticket.get("last_ai_gen"))
            email_post = ticket.get("post_email")
            note_post = ticket.get("post_note")
            field_put = ticket.get("put_fields")

            #if email_post is None or (email_post > 0 and email_post <= 3):
            #    post_email(arg_id, responses.get("email"))
            
            if note_post is None or (note_post > 0 and note_post <= 3):
                #Otherwise had responses.get("note")
                post_private_note(arg_id, responses)

            if field_put is None or (field_put > 0 and field_put <= 3):
                put_fields(arg_id) 

            get_conversations(arg_id)

        else:
            logs(f"Ticket ID# {arg_id} failed to pass post to FS filter")
            logs("End post to FS filter run.")

        logs("End test.")
        sys.exit(0)

    #^^^Used for test runs^^^

    while True:
        #Request functions for GET API's from Freshservice
        tickets = get_tickets()

        logs("Working on ticket batch. Getting requester and updating DB, adding tickets metadata to DB, and updating conversations field of the DB")
        for ticket in tickets:
            id = ticket.get("id")

            #Will grab the requester info from the ticket and put some of that data from FS and store that in the requesters table in the database.
            get_requester(ticket)
            add_tickets_table(ticket)

            get_conversations(id)

        #Will work on only having this run every X time the script loops.
        #get_departments()

        #Filters tickets based on if they exist and if there is values for AI first_response and private_note fields.
        logs("Filtering through batch of tickets.")

        #Filter tickets based off of time_last_message_sent field in the tickets table of the database. If empty, then ticket will added to first_response_tickets.
        filter_ai_response = filter_initial_tickets(tickets)

        #If is used to pass tickets that do not have a first response generated for them.
        if filter_ai_response:
            logs(f"Will now start working on generating AI responses for tickets that passed filter.")
            for ticket in filter_ai_response:
                id = ticket.get("id")
                logs(f"Working on generating AI responses for ticket ID# {id}")

                ticket = query_ticket(id)
                
                #Skips over ticket if no in list. Should have been in list from prior loop. So something went wrong if that's the case.
                if not ticket:
                    logs(f"Could not find ticket ID# {id} in database, skipping over it")
                    continue

                #first_response() returns a tuple... it returns the email for the user and the private note for the ticket, for the agent.
                responses = first_response(ticket)

            logs("End ai_response filter run.")

        else:
            logs("No tickets need AI generation right now")

        filter_post_fs = filter_post_to_fs(tickets)

        if filter_post_fs:
            for ticket in filter_post_fs:
                id = ticket.get("id")
                logs(f"Working on updating ticket in FreshService for ticket ID# {id}")

                ticket_class = query_ticket(id)
                
                responses = json.loads(ticket_class.get("last_ai_gen"))
                email_post = ticket_class.get("post_email")
                note_post = ticket_class.get("post_note")
                field_put = ticket_class.get("put_fields")

                email = responses.get("email")
                note = responses.get("note")

#                if email_post is None or (email_post > 0 and email_post <= 3):
#                    post_email(id, email)
                
                #This has been edited for demoing, would otherwise only post note but using for testing and just dumping the response json into the note field of the ticket.
                if note_post is None or (note_post > 0 and note_post <= 3):
                    post_private_note(id, responses)

                if field_put is None or (field_put > 0 and field_put <= 3):
                    put_fields(id) 

                get_conversations(id) 

            logs("End post to FS filter run.")

        else:
            logs("No tickets need updating on FreshService right now")

        n = 5
        logs(f"Sleeping for {n} seconds")
        time.sleep(n)

def runner():
    #Just starts the script and ends without dumping an error when exiting using Ctrl+c.
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting script")
