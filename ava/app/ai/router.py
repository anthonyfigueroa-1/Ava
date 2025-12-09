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
            relevant_articles = ai_articles(ticket)
        else:
            relevant_articles = None

        if query_tickets is True:
            relevant_tickets = ai_query_tickets(ticket)
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

            For deciding whether or not to query, base it off of complexity of the users request, whether or not the issue could be a recurring issue,
            whether the user is being vague, whether you believe that the topic at hand is something we have dealt with before on a prior ticket and/or have documented the environment or issue in the solutions article database.
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
                                "type": "string"
                                },
                            },
                        "query_articles": {
                            "type": "boolean",
                            "description": "Whether or not to query to knowledge base article table in the database."
                            },
                        "article_keywords": {
                            "type": "array",
                            "description": "If query_articles returns TRUE, then return keyword or keywords that would be most valuable to use with ILIKE in postgres to search in the title and description field for related solutions articles.",
                            "items": {
                                "type": "string"
                                },
                            },
                        "reasoning": {
                            "type": "string",
                            "description": "If either bool is False, give your reasoning",
                            }
                        },
                    "required": ["query_tickets", "ticket_keywords", "query_articles", "article_keywords", "reasoning"],
                    "additionalProperties": False
                    },
                },
            }
    return text
