from typing import final
from openai import OpenAI
import json, psycopg, os

from app.sql.tickets_db import query_tickets_ai
from app.logs import logs

tools = [
        {
            "type": "function",
            "name": "query_tickets",
            "description": "Takes name from input and searches for all past tickets in the database put in by the same user to check all of users prior tickets",
            "parameters": {
                "type": "object",
                "properties": {
                        "keywords": {
                            "type": "array",
                            "description": "Keyword or keywords that would be most valuable to use with ILIKE in postgres to search for the description field for related tickets",
                            "items": {
                                "type": "string"
                                },
                            },
                        },
                },
            "required": ["keywords"],
            }
        ]
        

instructions = 'Using json input, go ahead and user ticket info and requester name to query database of tickets. If requester name is null, return nothing to assist with skipping this entirely.'

def ai_query_tickets(ticket):
    key = os.environ["OPENAIKEY"]
    client = OpenAI(api_key=key)

    ins = [{"role": "user", "content": ticket}]

    logs("Querying tickets table for any relevant tickets")

    response = client.responses.create(
            model = "gpt-5",
            tools=tools,
            instructions=instructions,
            input=ins,
            )

    ins += response.output

    for item in response.output:
        if item.type == "function_call":
            if item.name == "query_tickets":
                args = json.loads(item.arguments)
                keywords = args.get("keywords")
                if keywords:
                    tickets = query_tickets_ai(keywords)
                else:
                    logs("Could not find any relevant tickets")
                    return

                ins.append({
                    "type": "function_call_output",
                    "call_id": item.call_id,
                    "output": json.dumps({
                            "tickets": tickets
                            })
                    })

    logs("Returning relevant tickets to AI agent for better response")
    return ins
