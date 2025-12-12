from openai import OpenAI, conversations
import json, os, tiktoken, random

from app.sql.tickets_db import query_tickets_ai, query_tickets_ai_slim
from app.logs import logs

tools = [
        {
            "type": "function",
            "name": "query_ids",
            "description": "Searches database for ticket ID's given and returns fat rows",
            "parameters": {
                "type": "object",
                "properties": {
                        "ids": {
                            "type": "array",
                            "description": "Top 3 ticket ID's that present the most relevant info to current ticket.",
                            "items": {
                                "type": "integer"
                                },
                            },
                        },
                    },
            "required": ["ids"],
            "additionalProperties": False,

            },
        {
            "type": "function",
            "name": "query_tickets_slim",
            "description": "Skim through tickets, returns skinny rows",
            "parameters": {
                "type": "object",
                "properties": {
                    "keywords": {
                        "type": "array",
                        "description": "Keyword or keywords that would be most valuable to use with ILIKE in postgres to search in the description or conversations field for related tickets",
                        "items": {
                            "type": ["string"]
                            },
                            },
                    "requester_email":{
                        "type": "string",
                        "description": "Email of requester to search for any old tickets put in by them."
                        },
                    "limits": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 50
                        },
                    },
            "required": ["keywords", "requester_name", "limits"],
            "additionalProperties": False
            },
        }
        ]
        
key = os.environ["OPENAIKEY"]
client = OpenAI(api_key=key)

instruct1 = """
Go ahead and use ticket info from the ticket json to query the database for tickets. 
Limit keyword strings list to top 3 keyword/keyword string.
If an 3rd-party ticket comes into our ticketing system, use the ticket ID of the 3rd-parties ticket, as one of the keywords, to search if any older tickets are related by ID.
For any tickets containing a bookings link, do your best to locate and reference the associated ticket connected to that booking.
"""

instruct2 = """ 
Using the given related slim tickets and comparing them to the current ticket, 
narrow down specific tickets that could be useful for generating a more tailored response back, in the request after this one.
Tickets don't have to be super related, anything that'll help point you in the right direction to help the next request tailor a better response.
"""

encoding = tiktoken.encoding_for_model("gpt-5")

def ai_query_tickets(ticket, keywords) -> list | None:
    logs("Starting search for any relevant tickets")
    slim_tickets = ai_query_slim(ticket, keywords)

    ticket_json = json.dumps(ticket, indent=4)

    ins = [{"role": "user", "content": f"Current ticket:\n{ticket_json}\n\nRelated Slim Tickets:\n{slim_tickets}"}]

    tokens = len(encoding.encode(str(ins)))
    logs(f"Token usage for related tickets: {tokens}")

    response = client.responses.create(
            model = "gpt-4.1",
            tools=tools,
            tool_choice= {"type": "function", "name":"query_ids"},
            instructions=instruct2,
            parallel_tool_calls=False,
            input=ins,
            )

    ins = []

    ins += ([{"role": "user", "content": ticket}])

    ins += response.output

    for item in response.output:
        if item.type == "function_call":
            if item.name == "query_ids":
                args = json.loads(item.arguments)
                ids = args.get("ids")
                if ids:
                    logs(f"Grabbing related tickets with ID#'s of {ids}", "info")
                    tickets = query_tickets_ai(ids)
                else:
                    logs("Could not find any relevant tickets")
                    return []

                if tickets:
                    logs("Returning relevant tickets to AI agent for better response")
                    tokens = len(encoding.encode(str(ticket)))
                    if tokens > 200000:
                        logs("Tickets exceeded token limit of 200,000! Will randomly remove one ticket")
                        tickets_num = (len(tickets) - 1)
                        num = random.randint(0, tickets_num)
                        tickets = tickets.pop(num)
                    return tickets 
                    
    logs("Query tickets failed right away")
    return [] 

def ai_query_slim(ticket: dict, keywords) -> list | None:
    id = ticket.get("id")
    requester_name = ticket.get("requester_name")
    tickets = query_tickets_ai_slim(keywords, id, requester_name)
    logs(f"Tickets found: {len(tickets)}", "info")

    return tickets
