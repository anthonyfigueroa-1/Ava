from fastapi import APIRouter, Depends, HTTPException
from redis import RedisError

from app.webhook.auth import check_token
from app.freshservice.tickets_api import get_ticket
from app.redis.redis_client import send_queue
from app.logs import logs
from app.redis import redis

router = APIRouter()

@router.post("/new_ticket")
def new_ticket(payload: dict, _: None = Depends(check_token)) -> dict:
    id = payload.get("id")
    ticket = get_ticket(id)
    logs(f"Recieved new ticket ID# {id}")
    send_queue(ticket, "new_ticket")
    return {"Successfully recieved new ticket id": id}

@router.put("/ticket_update")
def ticket_response(payload: dict, _: None = Depends(check_token)) -> dict:
    id = payload.get("id")
    ticket = get_ticket(id)
    logs(f"Recieved updated ticket ID# {id}")
    send_queue(ticket, "ticket_update")
    return {"Successfully recieved ticket response from": id}

@router.get("/redis_health")
def redis_health(_: None = Depends(check_token)) -> dict:
    try:
        return {"ok": True, "redis": redis.ping()}
    except RedisError as e:
        raise HTTPException(503, f"redis error: {e}")
