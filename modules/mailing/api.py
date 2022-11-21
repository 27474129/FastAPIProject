import logging
from modules.routers import mailing_router
from .schemas import Mailing
from .repository import MailingRepository, MessagesRepository
from .services import MailingService, StatsService
from celery_.celery import start_mailing
from pytz import timezone


logger = logging.getLogger(__name__)


@mailing_router.post("/")
async def create_mailing(mailing_data: Mailing):
    mailing_id = MailingRepository.create_mailing(mailing_data)
    mailing_data = MailingRepository.get_mailing_by_id(mailing_id)
    start_time = mailing_data.start_time

    # если нужно сразу запускать задачу т.к время старта уже пропущено
    if MailingService.check_start_time(start_time):
        logger.debug("start_time < current_time")
        start_mailing.delay(mailing_id)
    # если нужно ставить задачу на будущее исполнение
    else:
        logger.debug("start_time > current_time")
        zone = timezone("Europe/Moscow")
        start_time = zone.localize(start_time)
        # задача ставить в соответствии с start_time
        start_mailing.apply_async((mailing_id, ), eta=start_time)

    return {"success": True, "mailing_id": mailing_id}


@mailing_router.get("/")
async def get_mailing(mailing_id: int):
    mailing = MailingRepository.get_mailing_by_id(mailing_id)
    return {"success": True, "mailing": mailing}


@mailing_router.delete("/")
async def delete_mailing(mailing_id: int):
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
