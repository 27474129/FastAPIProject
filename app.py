import logging
from fastapi import FastAPI
from modules.clients.api import clients_router
from modules.mailing.api import mailing_router
from modules.errors_handler import errors_handler
from config import BASE_API_PREFIX


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


app = FastAPI()
app.include_router(clients_router)
app.include_router(mailing_router)


@app.get(f"{BASE_API_PREFIX}")
@errors_handler
async def root():
    return {"success": True}
