import os, json

from openai import OpenAI

from app.ai.query_db_tickets import ai_query_tickets
from app.ai.query_db_articles import ai_articles

key = os.environ["OPENAIKEY"]
client = OpenAI(api_key=key)

def query_db_router(ticket):
    response = query_db_request(ticket)

    if response:
        query_tickets = response.get("query_tickets")
        query_articles = response.get("query_articles")

        if query_articles is True:
            keyword = response.get("article_keyword")
            relevant_articles = ai_articles(ticket, keyword)
        else:
            relevant_articles = None

        if query_tickets is True:
            keywords = response.get("ticket_keywords")
            relevant_tickets = ai_query_tickets(ticket, keywords)
        else:
            relevant_tickets = None

        relevant_info = {
                "articles": relevant_articles,
                "tickets": relevant_tickets
                }

        return relevant_info
    
def query_db_request(ticket):
    text = query_db_json()

    instructions = """
            Based off the current ticket, decide whether or not it is necessary to query the database or not for relevant tickets or articles.
            If so return keyword(s) pulled from the current ticket that can be used to help query the database.

            Instructions for solutions article keyword: from the current ticket being given to you, pick the top keywords to search either the local database for related articles
            or for use to make an API call to Freshservice using the keyword. You're gonna want the keyword to be the best possible thing that'll match the ticket in terms of relevancy.
            Have keywords be singular words and not phrases. E.g not "Westin Outage" but instead "Westin" and/or "Outage".
            
            Instructions for tickets keywords: Go ahead and use ticket info from the ticket json to query the database for tickets. 
            If an 3rd-party ticket comes into our ticketing system, use the ticket ID of the 3rd-parties ticket, as one of the keywords, to search if any older tickets are related by ID.
            For any tickets containing a bookings link, do your best to locate and reference the associated ticket connected to that booking.
            Have keywords be singular words and not phrases. E.g not "Westin Outage" but instead "Westin" and/or "Outage".

            For deciding whether or not to query, base it off of complexity of the users request, whether or not the issue could be a recurring issue,
            whether the user is being vague, whether you believe that the topic at hand is something we have dealt with before on a prior ticket and/or have documented the environment or issue in the solutions article database.

            For reasoning, keep it to one detailed, concise paragraph.
        """

    input = [{
            "role": "user", 
            "content": json.dumps(ticket, indent=4)
            }]

    response = client.responses.create(
            model="gpt-4.1-mini",
            text=text,
            instructions=instructions,
            input=input
            )
    
    if response:
        if response.output:
            return json.loads(response.output_text)

def query_db_json() -> dict:
    text = {
            "format": {
                "type": "json_schema",
                "strict": True,
                "name": "response",
                "schema": {
                    "type": "object",
                    "properties": {
                        "query_tickets": {
                            "type": "boolean",
                            "description": "Whether or not to query to tickets table in the database."
                            },
                        "ticket_keywords": {
                            "type": "array",
                            "description": "If query_tickets returns TRUE, then return keyword or keywords that would be most valuable to use with ILIKE in postgres to search in the description or conversations field for related tickets.",
                            "items": {
                                "type": ["string", "null"]
                                },
                            },
                        "query_articles": {
                            "type": "boolean",
                            "description": "Whether or not to query to knowledge base article table in the database."
                            },
                        "article_keyword": {
                            "type": "array", 
                            "description": "If query_articles returns TRUE, then return keyword or keywords that would be most valuable to use with ILIKE in postgres to search in the description or conversations field for related articles.",
                            "items": {
                                "type": ["string", "null"]
                                },
                            },
                        "reasoning": {
                            "type": "string",
                            "description": "Give your reasoning on why or why not to query related tickets and/or solutions articles.",
                            }
                        },
                    "required": ["query_tickets", "ticket_keywords", "query_articles", "article_keyword", "reasoning"],
                    "additionalProperties": False
                    },
                },
            }
    return text
