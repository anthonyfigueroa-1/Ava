import os
from openai import OpenAI

tools = [
        {
            "type": "function",
            "name": "notify_agents",
            "description": "List of agents to email, because they are being requested in the ticket, by the requester.",
            "parameters": {
                "type": "object",
                "properties": {
                        "agents": {
                            "type": "array",
                            "description": "List of agents to email, because they are being requested in the ticket, by the requester.",
                            "items": {
                                "type": ["string", "null"]
                                },
                            },
                        },
                    },
            "additionalProperties": False,
            },
        ]

agent_dict = [{
                "Name": "Anthony Figueroa",
                "Email": "afigueroa@eastwest.com",
                },
              {
                  "Name": "Corbin Logan",
                  "Email": "clogan@eastwest.com",
                  },
              {
                  "Name": "Ben Lay",
                  "Email": "blay@eastwest.com",
                  },
              {
                  "Name": "Carlton Bowen",
                  "Email": "cbowen@eastwest.com",
                  },
              {
                  "Name": "Dalton Davis",
                  "Email": "ddavis@eastwest.com",
                  },
              {
                  "Name": "Earl Hartman",
                  "Email": "ehartman@eastwest.com",
                  },
              {
                  "Name": "Eric Mechling",
                  "Email": "emechling@eastwest.com",
                  },
              {
                  "Name": "Lawrence Moss",
                  "Email": "lmoss@eastwest.com",
                  },
              {
                  "Name": "Nathan Caldwell",
                  "Email": "ncaldwell@eastwest.com",
                  },
              {
                  "Name": "Ryan Stecher",
                  "Email": "rstecher@eastwest.com",
                  },
              {
                  "Name": "Sam Friedman",
                  "Email": "sfriedman@eastwest.com",
                  },
              {
                  "Name": "Shannon Sutter",
                  "Email": "ssutter@eastwest.com",
                  },
              {
                  "Name": "Will Fischer",
                  "Email": "wfischer@eastwest.com",
                  },
              ]

key = os.environ["OPENAIKEY"]
 
def private_note_notif():
   client = OpenAI(key)

   response = client.responses.create(

