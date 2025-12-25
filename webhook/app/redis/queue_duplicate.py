from datetime import datetime

import hashlib

from app.redis import redis
from app.freshservice.convo_api import get_convo

def queue_duplicate(ticket, ticket_type) -> bool:
    id = ticket.get("id")
    match ticket_type:
        case "new_ticket":
            is_new = redis.set(f"seen:{id}", "1", nx=True, ex=3600)
            if is_new is True:
                return True
            else:
                return False

        case "ticket_update":
            convo = get_convo(ticket.get("id"))
            newest_message = 0
            if isinstance(convo, list) is True:
                for message in convo:
                    created_at = message.get("created_at")
                    created_at = datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%SZ")
                    unix_created_at = int(created_at.timestamp())
                    if unix_created_at > newest_message:
                        newest_message = message.get("id")

            status = ticket.get("status")
            
            fingerprint = hashlib.sha256(f"{newest_message}{status}".encode()).hexdigest()
            
            is_new = redis.set(f"seen:{fingerprint}", "1", nx=True, ex=3600)
            if is_new is True:
                return True
            else:
                return False

        case _:
            return False
