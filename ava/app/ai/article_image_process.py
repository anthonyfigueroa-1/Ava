import json, os, re
from openai import BadRequestError, OpenAI

from app.sql.solution_articles_db import  query_article, update_img_metadata
from app.logs import logs
from app.ai import aap_instructions, aap_text

key = os.environ["OPENAIKEY"]

client = OpenAI(api_key=key)

def process_photos(article):
    id = article.get("id")
    title = article.get("title")
    description = article.get("description")

    metadata = check_photo_metadata(id)

    if metadata is True or not description:
        return

    re_images = re.findall(r'src\="([^"]+)"', description)

    if not re_images:
        return

    images = [] 
    for image in re_images:
        images.append(image)

    content = [{"type": "input_text", "text": description}]
    input = [{"role": "user", "content": content}]

    for image in images:
        content.append({"type": "input_image", "image_url": image})

    logs(f"Processing images into metadata for article {title}")

    try:
        response = client.responses.create(
               model="gpt-5.2",
                input=input,
                text=aap_text,
                instructions=aap_instructions,
                timeout=200
                )

    except BadRequestError:
        return

    if response.output_text:
        response = response.output_text

        images_metadata = json.loads(response)

        images = images_metadata.get("image_metadata")

        update_img_metadata(images, id)

    else:
        return

def check_photo_metadata(id):
    article = query_article(id)

    check = article.get("img_metadata")

    if not check:
        return False
    else:
        return True
