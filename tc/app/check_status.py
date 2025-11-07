from app.logs import logs
from app.sql.tickets import update_ticket_table
from app.freshservice.conversations import get_ticket_conversations

def check_status(ticket: dict):
    status = ticket.get("status")

    if status in (4, 5):
        conversation = get_ticket_conversations(ticket)
        update_ticket_table(ticket, conversation)
