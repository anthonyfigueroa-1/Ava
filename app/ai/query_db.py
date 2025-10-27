from typing import final
from openai import OpenAI
import json, psycopg, os

from app.sql.tickets_db import query_tickets

tools = [
        {
            "type": "function",
            "name": "query_tickets",
            "description": "Takes name from input and searches for all past tickets in the database put in by the same user to check all of users prior tickets",
            "parameters": {
                "type": "object",
                "properties": {
                    "requester_name": {
                        "type": ["string", "null"],
                        "description": "Name of the user used to query the database."
                        },
                    "keywords": {
                        "type": ["string", "null"],
                        "description": "Keyword or keywords that would be most valuable to use ILIKE in postgres for to search for related tickets in the description sections of other tickets in the database",
                        },
                    },
                "required": ["requester_name", "keywords"],
                },
            },
        ]

instructions = 'Using json input, go ahead and user ticket info and requester name to query database of tickets. If requester name is null, return nothing to assist with skipping this entirely.'

def ai_query_tickets(ticket):
    key = os.environ["OPENAIKEY"]
    client = OpenAI(api_key=key)

    ins = [{"role": "user", "content": ticket}]

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
                requester_name = args.get("requester_name")
                keywords = args.get("keywords")
                if requester_name and keywords:
                    tickets = query_tickets(requester_name, keywords)
                else:
                    return

                ins.append({
                    "type": "function_call_output",
                    "call_id": item.call_id,
                    "output": json.dumps({
                            "tickets": tickets
                            })
                    })

    return ins
