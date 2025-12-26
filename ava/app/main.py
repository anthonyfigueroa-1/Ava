import faulthandler, signal, sys
faulthandler.enable()
faulthandler.register(signal.SIGUSR1, file=sys.stderr, all_threads=True)

from app.freshservice.tickets_api import get_one_ticket_test, get_tickets
from app.sql.create_db import create_db
from app.sql.tickets_db import create_tickets_table, add_tickets_table
from app.sql.departments_db import create_departments_table
from app.sql.requesters_db import create_requesters_table
from app.logs import logs 
from app.filter import filter_initial_tickets, filter_post_to_fs
from app.arg_parse import parse_args
from app.sharepoint.ai_instructions import get_sp_instructions

import sys, time

def main():
    #Create arg parse to test individual tickets. 
    args = parse_args()
    arg_id = args.id if args.id else None
    updateai = args.updateai 

    if updateai is True:
        logs("Login to update AI instructions")
        get_sp_instructions()
        sys.exit(0)

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

            logs("Will now sort and check batch of tickets")
            ai_check = []
            fs_post_check = []
            for ticket in tickets:
                ai_response = filter_initial_tickets(ticket)
                ai_check.append(ai_response)

                post_to_fs = filter_post_to_fs(ticket)
                fs_post_check.append(post_to_fs)

            if True not in ai_check and True not in fs_post_check:
                logs("No tickets require Ava response nor require updating Freshservice right now")
                    
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
