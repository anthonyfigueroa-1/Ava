from azure.identity import DeviceCodeCredential
from azure.core import exceptions
from io import BytesIO
from docx import Document
import requests, os

from app.logs import logs

def get_bearer() -> str | None:
    try:
        credentials = DeviceCodeCredential(timeout=60)

        token = credentials.get_token("https://graph.microsoft.com/.default").token

        return token

    except exceptions.ClientAuthenticationError:
        return

def get_sp_instructions() -> str | None:
    bearer_token = get_bearer()

    if not bearer_token:
        instructions = load_cached_instructions()
        return instructions

    drive_id = os.environ["DRIVE_ID"]

    filepath = os.environ["SP_FILEPATH"]

    url = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/root:{filepath}:/content"

    header = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {bearer_token}"
            }
    try:
        response = requests.get(url=url, headers=header, timeout=(5,20))

        if not response.content:
            logs("Was not able to retrieve instructions form Tech Team SharePoint site")
            instructions = load_cached_instructions()
            return instructions

        logs("Succefully retrieved instructions from Tech Team SharePoint site")
        instructions = format_doc(response.content)

        if instructions:
            return instructions

        else:
            instructions = load_cached_instructions()
            return instructions

    except requests.exceptions.ReadTimeout:
        logs("Read Timeout Error occured while trying to connect to the Tech Team Sharepoint site")
        instructions = load_cached_instructions()
        return instructions

def format_doc(file) -> str | None:
    #File comes in in bytes and compressed, this allows me to uncompress the file and grab the text as readable text.
    file = BytesIO(file)
    doc = Document(file)

    #The following 5 lines saves each line as an entry in a list and then we join them together, seperating each line with \n and allowing me to return as a string."
    instructions = []

    if doc:
        for line in doc.paragraphs:
            instructions.append(line.text)

        save_instructions(instructions)

        instructions = '\n'.join(instructions)

        return instructions

    else:
        return

def save_instructions(instructions) -> None:
    with open("instructions.txt", "w") as file:
        for line in instructions:
            file.write(line + "\n")

def load_cached_instructions() -> str | None:
    line_list = []

    with open("instructions.txt", "r") as file:
        for line in file:
            line_list.append(line)

    if line_list:
        instructions = '\n'.join(line_list)
        logs("Loading cached instructions")
        return instructions

    else:
        return
