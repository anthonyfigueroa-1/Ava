from openai import OpenAI
import os

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
]
