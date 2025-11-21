from openai import OpenAI, conversations
import json, os, tiktoken

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
Using previous tools output, narrow down specific tickets that could be useful for generating a more tailored response back, in the request after this one.
Tickets don't have to be super related, anything that'll help point you in the right direction to help the next request tailor a better response.
"""

encoding = tiktoken.encoding_for_model("gpt-5")

def ai_query_tickets(ticket) -> list | None:
    logs("Starting search for any relevant tickets")
    ins = ai_query_slim(ticket)

    if ins:
        tokens = len(encoding.encode(str(ins)))
        logs(f"Token usage for related tickets: {tokens}")

        response = client.responses.create(
                model = "gpt-5",
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
                        tickets = query_tickets_ai(ids)
                    else:
                        logs("Could not find any relevant tickets")
                        return

                    if tickets:
                        neighbor_tickets = []
                        for ticket in tickets:
                            ticket = ticket[0]
                            conversations = ticket.get("conversations")
                            if conversations:
                                ticket["conversations"] = json.loads(conversations)

                            neighbor_tickets.append(ticket)

                        logs("Returning relevant tickets to AI agent for better response")
                        return neighbor_tickets 
                        
                    else:
                        logs("Query tickets failed")
                        return []



    logs("Query tickets failed right away")
    return [] 

def ai_query_slim(ticket: dict) -> list | None:
    ins = [{"role": "user", "content": ticket}]

    response = client.responses.create(
            model = "gpt-5",
            tools=tools,
            tool_choice= {"type": "function", "name":"query_tickets_slim"},
            instructions=instruct1,
            parallel_tool_calls=False,
            input=ins,
            )

    ins += response.output

    for item in response.output:
        if item.type == "function_call":
            if item.name == "query_tickets_slim":
                args = json.loads(item.arguments)
                keywords = args.get("keywords")
                limits = args.get("limits")
                requester_name = args.get("requester_name")
                if keywords and limits:
                    dict_ticket = json.loads(ticket)
                    id = dict_ticket.get("id")
                    tickets = query_tickets_ai_slim(keywords, id, requester_name, limits)
                else:
                    logs("Could not find any relevant tickets")
                    return

                if tickets:
                    ins.append({
                        "type": "function_call_output",
                        "call_id": item.call_id,
                        "output": json.dumps({
                                "tickets": tickets
                                })
                        })
                else:
                    ins = []

    return ins


