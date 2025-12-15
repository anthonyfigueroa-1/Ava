import os, json
from openai import OpenAI

from app.ai import resolution_note_instructions, resolution_note_json

api_key = os.environ["OPENAIKEY"]
client = OpenAI(api_key=api_key)

def ai_resolution_note(ticket):
    ins = [{
        "role": "user",
        "content": json.dumps(ticket, indent=4)
        }]

    response = client.responses.create(
            model="gpt-4o-mini",
            instructions=resolution_note_instructions,
            input=ins,
            text=resolution_note_json, 
            )

    if response:
        if response.output_text:
            resolution_note = response.output_text
            resolution_note = json.loads(resolution_note)
            resolution_note = resolution_note.get("resolution_note")
            
            if resolution_note:

