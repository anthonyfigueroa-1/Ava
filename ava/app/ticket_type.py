import re
from app.freshservice.offboarding_form_api import get_offboarding_form
from app.freshservice.onboarding_form_api import get_onboarding_form
from app.freshservice.service_request_api import get_service_request_info

def check_if_service_request(ticket):
    ticket_type = ticket.get("type")
    subject = ticket.get("subject")

    if ticket_type == "Service Request":
        onboarding = re.match(r"Employee Onboarding Request for .+ in division", subject, re.IGNORECASE)
        offboarding = re.match(r"Employee Offboarding Request for .+ in division", subject, re.IGNORECASE)
        if onboarding:
            get_onboarding_form(ticket)
        elif offboarding:
            get_offboarding_form(ticket)
        else:
            get_service_request_info(ticket)
