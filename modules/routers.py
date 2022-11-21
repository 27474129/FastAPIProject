from fastapi import APIRouter
from config import BASE_API_PREFIX

# под каждый модуль свой роутер
clients_router = APIRouter(prefix=f"{BASE_API_PREFIX}/clients")
mailing_router = APIRouter(prefix=f"{BASE_API_PREFIX}/mailing")
