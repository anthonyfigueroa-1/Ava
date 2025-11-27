from app.freshservice.conversations_api import get_conversations
from openai import OpenAI, BadRequestError
import os, json, tiktoken

from app.logs import logs
from app.regex import get_images
from app.sql.tickets_db import query_ticket_response, add_ai_response, query_ticket
from app.ai.query_db_tickets import ai_query_tickets
from app.ai.query_db_articles import ai_articles
from app.ai.conversations import convo_user_id_convert
from app.ai import instructions

next_step = "If 'NO AI NEEDED' and agent responded back to ticket, generate what the follow up email would be to the user of ticket and what other note you would leave the agent in here as well."

text = {
        "format": {
            "type": "json_schema",
            "strict": True,
            "name": "response",
            "schema": {
                "type": "object",
                "properties": {
                    "email": {"type": "string"},
                    "note": {
                        "type": ["string", "null"],
                        "description": "Note for ticket, or null if note is not needed"
                        },
                    "next_steps": {
                        "type": ["string", "null"],
                        "description": next_step
                        }
                    },
                "required": ["email", "note", "next_steps"],
                "additionalProperties": False
                },
            },
        }

encoding = tiktoken.encoding_for_model("gpt-5")

def first_response(ticket):
    bad_img = f"""{instructions} \n(This is a special instruction... You are recieving this because an image(s) failed to import so a new OPENAI api request needs to be made without the images.) 
    If this is the case, take a look at raw_description of the json I am inputting. If there is 'src img' section, look to see if it is located within the signature or body of the description. 
    If it is in the signature, ignore it and don't mention it, if it is in the body, let the user know that their image did not get recieved properly and for them to resend it."""

    key = os.environ["OPENAIKEY"]
    client = OpenAI(api_key=key)

    id = ticket.get("id")

    #Use ticket database row info to feed into openai to avoid bloat. Feeding in as json still.
    ticket = query_ticket_response(id)

    ticket_string = json.dumps(ticket)

    check_priority(ticket)

    """Need to move below elsewhere to allow me to process to metadata"""
    images = get_images(ticket.get("raw_description"))

    #Will use AI to get most related solution articles and tickets found in DB
    related_articles = ai_articles(ticket_string)
    ticket_neighbors = ai_query_tickets(ticket_string)

    #Getting convo's one more time to ensure that Ava does not respond after agent has already messaged back on ticket.
    get_conversations(id)

    #Creating list to get all user_id's that sent a message on current and related tickets.
    ticket_user_convert = [ticket]
    for ticket in ticket_neighbors:
        ticket_user_convert.append(ticket)

    #Converts user_id's, if possible, to allow Ava to draw similarities to who's id is who's.
    users_in_convo = convo_user_id_convert(ticket_user_convert)

    ins = {
            "current_ticket":{
                "description": "Current ticket you are working on writing a response for.",
                "ticket": ticket,
                },
            "related_tickets":{
                "description": "Tickets found in database to be most relevant to current ticket.",
                "tickets": ticket_neighbors,
                },
            "related_articles":{
                "description": "KB articles found in database and to be most relevant to current ticket.",
                "articles": related_articles,
                },
            "user_id_ref": {
                "description": "Refernce JSON of user_id's mentioned to assist with tying user_id to a name, if applicable.",
                "users:": users_in_convo,
                },
            }

    #Got rid of str()
    ins = json.dumps(ins)

    input = [{"role": "user", "content": ins}]

    tokens = len(encoding.encode(ins))

    logs(f"Token usage for response back: {tokens}")

    if images:
        try:
            content = [{"type": "input_text", "text": ins}]
            input = [{
                        "role": "user",
                        "content": content,
                        }]

            seperate_images(images, content)

            response = client.responses.create(
                    model="gpt-5",
                    instructions=instructions,
                    input= input,
                    text=text,
                    timeout=100
                    )

        except BadRequestError:
            response = client.responses.create(
                model="gpt-5",
                instructions=bad_img,
                input=ins,
                text=text,
                timeout=100
                )
    else:
        response = client.responses.create(
                model="gpt-5",
                instructions=instructions,
                input=input,
                text=text,
                timeout=100
                )

    response = response.output_text

    if response:
        logs(f"Response generated.")
        response = json.loads(response)
    else:
        logs(f"No response generated by OPENAI.")

    check_if_first_response(response, id)

def check_if_first_response(responses, ticket_id):
    if not responses:
        text = (f"No AI Response generated for ticket ID# {ticket_id}")

        logs(text)

        #Find out amount of attempts and tack onto counter how many attempts have been made.
        logs(f"Querying ticket ID# {ticket_id} for updating ai_response attempts")

        ticket = query_ticket(ticket_id)

        attempts = ticket.get("ai_attempts")
        if not attempts:
            attempts = 1
        else:
            attempts += 1

        add_ai_response(text, attempts, ticket_id)

    email = responses.get("email")

    if "NO AI NEEDED" in email:
        logs(f"NO AI NEEDED for ticket ID# {ticket_id}")
        attempts = 10
        add_ai_response(responses, attempts, ticket_id)

    elif responses:
        #No extra attempts needed for generating ai response
        attempts = 0
        add_ai_response(responses, attempts, ticket_id)

def seperate_images(images, content):
    for image in images:
        ai_json = {
                    "type": "input_image",
                    "image_url": image,
                    }

        content.append(ai_json)

def check_priority(ticket) -> None:
    p_dict = {
            1: "Low",
            2: "Medium",
            3: "High",
            4: "Urgent"
            }

    priority = ticket.get("priority")
    
    for p in p_dict:
        if priority == p:
            priority = p_dict[p]

    ticket["priority"] = priority
