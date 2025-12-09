import re
from app.freshservice.offboarding_form_api import get_offboarding_form
from app.freshservice.onboarding_form_api import get_onboarding_form
from app.freshservice.service_request_api import get_service_request_info
from app.logs import logs

def check_if_service_request(ticket):
    id = ticket.get("id")
    ticket_type = ticket.get("type")
    subject = ticket.get("subject")

    service_request = re.search(r"Service Request", ticket_type, re.IGNORECASE)
    if service_request:
        logs(f"Ticket ID# {id} is of type 'Service Request'")
        onboarding = re.search(r"Employee Onboarding Request for .+ in division", subject, re.IGNORECASE)
        offboarding = re.search(r"Employee Offboarding Request for .+ in division", subject, re.IGNORECASE)
        if onboarding:
            logs(f"Getting onboarding form for ticket ID# {id}")
            get_onboarding_form(ticket)
        elif offboarding:
            logs(f"Getting offboarding form for ticket ID# {id}")
            get_offboarding_form(ticket)
        else:
            logs(f"Getting service request form for ticket ID# {id}")
            get_service_request_info(ticket)
