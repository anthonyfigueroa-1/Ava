from fastapi import FastAPI

from app.webhook.routes import router

app = FastAPI()
app.include_router(router=router)
