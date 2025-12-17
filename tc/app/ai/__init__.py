resolution_note_instructions="""
NOTE: FORMAT ALL 'resolution_note' OUTPUT AS HTML FOR BETTER STRUCTURE AND READABILITY.

You will be given either one of two things, either a resolution note from a ticket or a ticket row from the database.

If you recieve only a resolution note, go ahead and word it better if possible, be conservative on these, if nothing needs
to change, just return the note back with no changes.

If you recieve a ticket row, which I will pass in using Python's json.dumps as to turn it into a string, go ahead and using
all of the info given, summarize the ticket. Mainly focus on using the title, description, and conversation to base your
summarization off of. This summarization will be the new resolution note of the ticket. If a ticket has little or no info to
go off of, you can state that in the summary. The summary doesn't need to be detailed unless a ticket is complex and justifies
a long summary.

Gaurdrails:
- Do not make up anything that has not happened, only base resolution notes off info being given.
"""

resolution_note_json = {
        "format": {
            "type": "json_schema",
            "name": "response",
            "schema": {
                "type": "object",
                "properties": {
                    "resolution_note": {
                        "type": "string",
                        "description": "A private note that summarizes the ticket and ticket convo. into a neat, readable, resolution note."
                    },
                },
            "required": ["resolution_note"],
            "additionalProperties": False
            },
            "strict": True,
            }
        }
