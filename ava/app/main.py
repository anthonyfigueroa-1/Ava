import faulthandler, signal, sys
faulthandler.enable()
faulthandler.register(signal.SIGUSR1, file=sys.stderr, all_threads=True)

from app.freshservice import email_api
from app.freshservice.tickets_api import get_one_ticket_test, get_tickets, get_one_ticket
from app.freshservice.departments_api import get_departments
from app.freshservice.email_api import post_email
from app.freshservice.private_note_api import post_private_note
from app.freshservice.conversations_api import get_conversations
from app.freshservice.fields_api import put_fields
from app.sql.create_db import create_db
from app.sql.tickets_db import add_requesters, create_tickets_table, add_tickets_table, query_ticket
from app.sql.departments_db import create_departments_table
from app.sql.requesters_db import create_requesters_table
from app.ai.responses import first_response
from app.logs import logs 
from app.filter import filter_initial_tickets, filter_ai_response_test, filter_post_to_fs, filter_post_to_fs_test
from app.arg_parse import parse_args
from app.sharepoint.ai_instructions import get_sp_instructions, load_cached_instructions

import sys, time, json

def main():
    #Create arg parse to test individual tickets. 
    args = parse_args()
    arg_id = args.id if args.id else None
    updateai = args.updateai 

    if updateai is True:
        logs("Login to update AI instructions")
        instructions = get_sp_instructions()
        sys.exit(0)
    else:
        instructions = load_cached_instructions()

    if not instructions:
        logs("Exiting because no instructions for the AI bot were able to be loaded in")
        sys.exit(5)

    #functions to create the database and the tables for the databases
    create_db()
    create_tickets_table()
    create_departments_table()
    create_requesters_table()
    logs("All tables were either successfully created or already existed in database.")


    while True:
        #Request functions for GET API's from Freshservice
        if arg_id:
            ticket = get_one_ticket_test(arg_id)
            logs("Running test run")
            tickets = [ticket]

        else:
            tickets = get_tickets()

        if tickets:
            add_tickets_table(tickets)

            #Will work on only having this run every X time the script loops.
            #get_departments()

            #Filter tickets based off of time_last_message_sent field in the tickets table of the database. If empty, then ticket will added to first_response_tickets.
            logs("Filtering through batch of tickets.")
            filter_ai_response = filter_initial_tickets(tickets)

            #If is used to pass tickets that do not have a first response generated for them.
            if filter_ai_response:
                logs(f"Will now start working on generating AI responses for tickets that passed filter.")
                for ticket in filter_ai_response:
                    id = ticket.get("id")

                    get_conversations(id)
                    add_requesters(tickets)

                    logs(f"Working on generating AI responses for ticket ID# {id}")

                    ticket = query_ticket(id)
                    
                    #Skips over ticket if no in list. Should have been in list from prior loop. So something went wrong if that's the case.
                    if not ticket:
                        logs(f"Could not find ticket ID# {id} in database, skipping over it")
                        continue

                    #first_response() returns a tuple... it returns the email for the user and the private note for the ticket, for the agent.
                    responses = first_response(ticket, instructions)

                logs("End ai_response filter run.")

            else:
                logs("No tickets need AI generation right now")

            filter_post_fs = filter_post_to_fs(tickets)

            if filter_post_fs:
                for ticket in filter_post_fs:
                    id = ticket.get("id")
                    logs(f"Working on updating ticket in FreshService for ticket ID# {id}")
                    get_one_ticket(id)

                    ticket = query_ticket(id)

                    field_put = ticket.get("put_fields")
                    ai_email = json.loads(ticket.get('ai_email'))
                    ai_note = json.loads(ticket.get('ai_note'))
                    ai_next_steps = json.loads(ticket.get('ai_next_steps'))

                    email_attempts = ai_email.get('attempts')
                    note_attempts = ai_note.get('attempts')
                    next_steps_attempts = ai_next_steps.get('attempts')

                    if email_attempts is None or (email_attempts > 0 and email_attempts <= 3):
                        post_email(ticket, ai_email)
                    
                    if note_attempts is None or (note_attempts > 0 and note_attempts <= 3):
                        post_private_note(id, ai_note)

                    if next_steps_attempts is None or (next_steps_attempts > 0 and next_steps_attempts <= 3):
                        post_private_note(id, ai_next_steps)

                    if field_put is None or (field_put > 0 and field_put <= 3):
                        put_fields(id) 

                logs("End post to FS filter run.")

            else:
                logs("No tickets need updating on FreshService right now")
        
        else:
            logs("Skipping all steps in script since tickets failed to be grabbed")
        
        if arg_id:
            logs("Finished test run")
            sys.exit(0)
        n = 15
        logs(f"Sleeping for {n} seconds")
        time.sleep(n)

def runner():
    #Just starts the script and ends without dumping an error when exiting using Ctrl+c.
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting script")
