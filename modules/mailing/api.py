"""
    Всё время указывается как московское
"""
import logging
from modules.routers import mailing_router
from .schemas import Mailing
from .repository import MailingRepository, MessagesRepository
from .services import MailingService, StatsService, CeleryService
from celery_.celery import start_mailing
from pytz import timezone
from celery_.celery import app


logger = logging.getLogger(__name__)


@mailing_router.post("/")
async def create_mailing(mailing_data: Mailing):
    mailing_id = MailingRepository.create_mailing(mailing_data)
    mailing_data = MailingRepository.get_mailing_by_id(mailing_id)
    start_time = mailing_data.start_time

    zone = timezone("Europe/Moscow")
    start_time = zone.localize(start_time)
    start_mailing.apply_async((mailing_id,), eta=start_time, task_id=str(mailing_id))
    return {"success": True, "mailing_id": mailing_id}


@mailing_router.get("/")
async def get_mailing(mailing_id: int):
    mailing = MailingRepository.get_mailing_by_id(mailing_id)
    return {"success": True, "mailing": mailing}


@mailing_router.delete("/")
async def delete_mailing(mailing_id: int):
    app.control.revoke(str(mailing_id))
    mailing = MailingRepository.get_mailing_by_id(mailing_id)
    MailingRepository.delete_mailing(mailing_id)
    return {"success": True, "deleted_mailing": mailing}


@mailing_router.put("/")
async def update_mailing(mailing_data: Mailing):
    MailingRepository.update_mailing(mailing_data)
    return {"success": True, "new_mailing": mailing_data}


# view общей статистики
@mailing_router.get("/stats")
async def get_base_stats():
    mailings = MailingRepository.get_all_mailings()
    return {"success": True, "stats": StatsService.get_base_stats(mailings)}


# view статистики по конкретной рассылки
@mailing_router.get("/stats/{mailing_id}")
async def get_stats_for_mailing(mailing_id: int):
    messages = MessagesRepository.get_mailing_messages(mailing_id)
    stats = StatsService.get_stats_for_mailing(mailing_id, messages)
    return {"success": True, "base_stats": stats}
