resolution_note_instructions=""" ... """

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
