import logging
from modules.routers import clients_router
from .schemas import Client
from .repository import ClientsRepository


logger = logging.getLogger(__name__)


@clients_router.post("/")
async def create_client(client_data: Client):
    client_id = ClientsRepository.create_client(client_data)
    return {"success": True, "client_id": client_id}


@clients_router.delete("/")
async def delete_client(client_id: int):
    client = ClientsRepository.get_client_by_id(client_id)
    ClientsRepository.delete_client(client_id)
    return {"success": True, "deleted_client": client}


@clients_router.put("/")
async def update_client(client_id: int, client_data: Client):
    ClientsRepository.update_client(client_id, client_data)
    return {"success": True, "updated_client": client_data}


@clients_router.get("/{id}")
async def get_client(client_id: int):
    client = ClientsRepository.get_client_by_id(client_id)
    return {"success": True, "client": client}
