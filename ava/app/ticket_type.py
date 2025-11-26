def check_if_service_request(ticket):
    ticket_type = ticket.get("type")

    if ticket_type == "Service Request":
        return True
