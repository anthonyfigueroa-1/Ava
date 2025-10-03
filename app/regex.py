import re

def seperate_responses(ai_response):
    match = re.search(r"Email\:(.*)Private Note:(.*)", ai_response, re.DOTALL)

    if match:
        print("\n")
        response = (match.group(1).strip(), match.group(2).strip())
        return response
