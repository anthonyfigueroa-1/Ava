from fastapi import APIRouter, Depends
from app.webhook.auth import check_token

router = APIRouter()

@router.post("/new_ticket")
def new_ticket(payload: dict, _: None = Depends(check_token)):
    print(payload)
    id = payload.get("id")
    return {"Successfully recieved new ticket id": id}

@router.put("/ticket_update")
def ticket_response(payload: dict, _: None = Depends(check_token)):
    print(payload)
    id = payload.get("id")
    return {"Successfully recieved ticket response from": id}
