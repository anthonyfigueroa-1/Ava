from openai import OpenAI
import json, os, tiktoken, random

from app.sql.tickets_db import query_tickets_ai, query_tickets_ai_slim
from app.logs import logs
from app.ai import ticket_sql_instructions, ticket_sql_tools
       
key = os.environ["OPENAIKEY"]
client = OpenAI(api_key=key)

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
            tools=ticket_sql_tools,
            tool_choice= {"type": "function", "name":"query_ids"},
            instructions=ticket_sql_instructions,
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
