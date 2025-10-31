import re

def seperate_responses(ai_response):
    match = re.search(r"Email\:(.*)Private Note:(.*)", ai_response, re.DOTALL)

    if match:
        responses = (match.group(1).strip(), match.group(2).strip())
        return responses

def get_images(raw_description):
    match = re.findall(r'img\ssrc\=\"([^"]+)\"', raw_description)

    return match
