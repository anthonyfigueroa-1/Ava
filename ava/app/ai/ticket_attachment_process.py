import re, openai, os 

from app.regex import get_images
from app.sql.tickets_db import add_metadata
from app.ai import tap_instructions, tap_text

key = os.environ["OPENAIKEY"]
client = openai.OpenAI(api_key=key)

def ticket_attachments_process(ticket):
    print("grabbing imagse")
    id = ticket.get("id")
    ticket_json = ticket.get("json")
    attachments = (ticket_json.get("attachments"))
    subject = ticket.get("subject")
    description = ticket.get("description")
    raw_description = ticket.get("raw_description")

    input = [
            {
                "type": "input_text",
                "text": f"Current ticket... Subject: {subject} Description: {description}"
                }
            ]

    content = []

    #Getting images stored into description instead of being attached
    seperate_images(raw_description, content)
    
    #Get url's from attachments
    #No need to return content since lists are emutable
    get_attachment_urls(attachments, content)

    if content:
        input += content
        response = get_ai_attachment_response(input)

        if response:
            if response.output_text:
                add_metadata(response.output_text, id)
           
def seperate_images(raw_description, content):
    images = get_images(raw_description)
    if images:
        print("got images from desc")
        for image in images:
            ai_json = {
                        "type": "input_image",
                        "image_url": image,
                        }
            content.append(ai_json)

def get_attachment_urls(attachments: list[dict], content: list[dict]):
    if attachments:
        for item in attachments:
            item_name = item.get("name")
            url = item.get("attachment_url")
            img = re.search(r"\.png|\.jpg|\.jpeg", item_name, re.IGNORECASE)
            pdf = re.search(r"\.pdf", item_name, re.IGNORECASE)
            if img:
                content.append({
                    "type": "input_image",
                    "image_url": url
                    })
            if pdf:
                content.append({
                    "type": "input_file",
                    "file_url": url
                    })

def get_ai_attachment_response(content):
    ins = [
        {
            "role": "user",
            "content": content
            }
        ]

    try:
        response = client.responses.create(
                model="gpt-5.2",
                instructions=tap_instructions,
                input=ins,
                text=tap_text
                )
        print(response)

        if response:
            return response

    except openai.BadRequestError:
        pass 
