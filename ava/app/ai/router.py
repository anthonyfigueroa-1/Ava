import os, json

from openai import OpenAI

from app.ai.query_db_tickets import ai_query_tickets
from app.ai.query_db_articles import ai_articles
from app.ai import router_instructions, router_text

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
    input = [{
            "role": "user", 
            "content": json.dumps(ticket, indent=4)
            }]

    response = client.responses.create(
            model="gpt-4.1-mini",
            text=router_text,
            instructions=router_instructions,
            input=input
            )
    
    if response:
        if response.output:
            return json.loads(response.output_text)
