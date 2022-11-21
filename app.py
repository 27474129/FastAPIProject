import logging
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from modules.clients.api import clients_router
from modules.mailing.api import mailing_router
from config import BASE_API_PREFIX


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


app = FastAPI()
app.include_router(clients_router)
app.include_router(mailing_router)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="MailingAPI",
        version="1",
        description="Тестовое задание, API для рассылки",
        routes=app.routes,
    )
    app.openapi_schema = openapi_schema

    return app.openapi_schema


app.openapi = custom_openapi


@app.get(f"{BASE_API_PREFIX}")
async def root():
    return {"success": True}
