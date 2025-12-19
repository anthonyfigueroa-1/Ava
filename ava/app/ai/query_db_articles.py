import json, os, tiktoken, random
from openai import OpenAI

from app.sql.solution_articles_db import ai_query_articles_id, query_article, ai_query_articles_slim
from app.freshservice.solution_articles import get_some_articles, search_articles
from app.ai.article_image_process import process_photos
from app.logs import logs
from app.ai import article_sql_tools, article_sql_instructions

key = os.environ["OPENAIKEY"]

client = OpenAI(api_key=key)

encoding = tiktoken.encoding_for_model("gpt-5")

def ai_articles(ticket, keyword):
    logs("Starting search for relevant Solutions Articles")
    
    ticket_json = json.dumps(ticket, indent=4)

    slim_articles = ai_articles_slim(keyword)
   
    ins = [{"role": "user", "content": f"Current ticket:\n{ticket_json}\n\nRelated slim articles:\n{slim_articles}"}] 

    tokens = len(encoding.encode(str(ins)))

    logs(f"Tokens of input for articles: {tokens}")

    response = client.responses.create(
            model="gpt-4.1",
            input=ins,
            tools=article_sql_tools,
            tool_choice={"type": "function", "name": "ai_query_articles"},
            instructions=article_sql_instructions,
            parallel_tool_calls=False,
            )

    for item in response.output:
        if item.type == "function_call":
            if item.name == "ai_query_articles":
                args = json.loads(item.arguments)
                ids = args.get("ids")

                if ids:
                    logs(f"Grabbing related articles with ID#'s of {ids}", "info")
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


def ai_articles_slim(keywords):
    search_articles(keywords)
    articles = ai_query_articles_slim(keywords)

    if articles:
        logs(f"Articles found: {len(articles)}", "info")
        slim_articles = []
        for article in articles:
            article = article[0]
            article = query_article(article.get("id"))
            article["img_metadata"] = ""
            slim_articles.append(article)

        return json.dumps(slim_articles) 
