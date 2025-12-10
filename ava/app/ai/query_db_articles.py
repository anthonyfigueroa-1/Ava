import json, os, tiktoken, random
from openai import OpenAI

from app.sql.solution_articles_db import ai_query_articles_id, query_article, ai_query_articles_slim
from app.freshservice.solution_articles import get_some_articles, search_articles
from app.ai.article_image_process import process_photos
from app.logs import logs

key = os.environ["OPENAIKEY"]

client = OpenAI(api_key=key)

tools = [
{
            "type": "function",
            "name": "ai_query_articles_slim",
            "description": "Searches database for knowledge base solutions articles for relevant ",
            "parameters": {
                "type": "object",
                "properties": {
                        "keyword": {
                            "type": "string",
                            "description": "Top keyword, based on current ticket, to search for KB articles by, can be a string of keywords, e.g. 'Westin Opera'",
                            },
                        },
                    },
            "required": ["keyword"],
            "additionalProperties": False,
            },
{
            "type": "function",
            "name": "ai_query_articles",
            "description": "Uses previous response.output to find, up to, the top 2 KB articles related to the current ticket.",
            "parameters": {
                "type": "object",
                "properties": {
                    "ids": {
                        "type": "array",
                        "description": "Array of top 2 KB article ID's to use for refined similar articles.",
                        "items": {
                            "type": "integer",
                            "description": "KB article ID."
                            },
                        },
                    },
                "required": ["ids"],
                "additionalProperties": False,
                },
            }
]

slim_instructions="""
From the current ticket being given to you, pick the top keyword to search either the local database for related articles
or for use to make an API call to Freshservice using the keyword. The keyword can be a string of words if needed.
You're gonna want the keyword to be the best possible thing that'll match the ticket in terms of relevancy.
"""

fat_instructions="""
From the list of solutions articles you have been given in related slim articles, go ahead and refine the articles.
Choose the top 2 article ID's that are the absolute closest in regards to relevance to the current ticket.
If a tie is met, have the newest article be the tie breaker.

If the current ticket at hand is about phishing/spam email(s), an example being a ticket of a user forwarding an email to us asking about whether or not the
email is spam/phishing, add on a 3rd article into the array, with the ID of that being 5000101148.

If the current ticket at hand is about installing an application onto their computer, an example being a ticket of a user requesting IT to install or provide Admin Credentials
to go ahead and approve the install of FoxIt or Axis Camera app. In this case, add on a 3rd article into the array, with the ID of that being 5000101261.
"""

encoding = tiktoken.encoding_for_model("gpt-5")

def ai_articles(ticket, keyword):
    logs("Starting search for relevant Solutions Articles")
    
    ticket_json = json.dumps(ticket, indent=4)

    slim_articles = ai_articles_slim(ticket_json, keyword)
   
#    if not ins:
#        message = f"No relevant articles were able to be found"
#        logs(message)
#        return message

    ins = [{"role": "user", "content": f"Current ticket:\n{ticket_json}\n\nRelated slim articles:\n{slim_articles}"}] 

    tokens = len(encoding.encode(str(ins)))

    logs(f"Tokens of input for articles: {tokens}")

    response = client.responses.create(
            model="gpt-4.1",
            input=ins,
            tools=tools,
            tool_choice={"type": "function", "name": "ai_query_articles"},
            instructions=fat_instructions,
            parallel_tool_calls=False,
            )

    for item in response.output:
        if item.type == "function_call":
            if item.name == "ai_query_articles":
                args = json.loads(item.arguments)
                ids = args.get("ids")

                if ids:
                    print(f"Grabbing related articles with ID#'s of {ids}")
                    articles = ai_query_articles_id(ids)

                    if not articles:
                        logs(f"Could not find articles with IDs of {ids} in local DB, going to grab them from FS instead.")
                        articles = get_some_articles(ids)

                    if articles:
                        tokens = len(encoding.encode(str(articles)))
                        if tokens > 200000:
                            logs("Articles exceeded token limit of 200,000! Will randomly remove one article")
                            article_num = (len(articles) - 1)
                            num = random.randint(0, article_num)
                            articles = articles.pop(num)
                        for article in articles:
                            article = article[0]
                            process_photos(article)
                        
                        logs(f"Returning relevant articles for better response back")
                        return articles


def ai_articles_slim(ticket, keyword):
#    ins = [{"role": "user", "content": ticket}]
#
#    response = client.responses.create(
#            model="gpt-5",
#            input=ins,
#            tools=tools,
#            tool_choice={"type": "function", "name": "ai_query_articles_slim"},
#            instructions=slim_instructions,
#            parallel_tool_calls=False,
#            )
#
#    ins += response.output
#
#    for item in response.output:
#        if item.type == "function_call":
#            if item.name == "ai_query_articles_slim":
#                args = (json.loads(item.arguments))
#                keyword = args.get("keyword")
#
#                if keyword:
    articles = search_articles(keyword)
    articles = ai_query_articles_slim(keyword)
#                    
#                    #if not articles:
#                        #logs("Was not able to find any relevant articles for this ticket in the local DB, going to search FS now")

    if articles:
        slim_articles = []
        for article in articles:
            article = article[0]
            article = query_article(article.get("id"))
            article["img_metadata"] = ""
            slim_articles.append(article)

#                        ins.append({
#                            "type": "function_call_output",
#                            "call_id": item.call_id,
#                            "output": json.dumps({
#                                "kb_articles": slim_articles
#                                })
#                            })

        return json.dumps(slim_articles) 
