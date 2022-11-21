import json
import requests
import config
from .schemas import Message, Mailing
from modules.clients.repository import ClientsRepository
from modules.mailing.repository import MessagesRepository
from modules.context_managers import Postgresql
from modules.mailing.repository import MailingRepository
from celery.utils.log import get_task_logger
from datetime import datetime
from pytz import timezone


logger = get_task_logger(__name__)


class MailingService:
    __slots__ = ["mailing_id", "headers", "start_time", "message", "filters", "end_time"]

    def __init__(self, mailing_id: int):
        self.mailing_id = mailing_id
        self.headers = {"Authorization": f"Bearer {config.BEARER_TOKEN}"}

        mailing_data = MailingRepository.get_mailing_by_id(self.mailing_id)
        self.start_time = mailing_data.start_time
        self.message = mailing_data.message
        self.filters = mailing_data.filters
        self.end_time = mailing_data.end_time

    # False - задачу нужно сразу запускать
    # True - задача ставиться на крон
    @staticmethod
    def check_start_time(start_time: datetime):
        return False if not MailingService.compare_time(start_time) else True

    @staticmethod
    def compare_time(time: datetime) -> bool:
        zone = timezone("Europe/Moscow")
        time = zone.localize(time)
        if datetime.now(tz=timezone("Europe/Moscow")) > time:
            return True
        elif datetime.now(tz=timezone("Europe/Moscow")) < time:
            return False

    def start_mailing(self):
        clients = ClientsRepository.get_clients()
        if not MessagesRepository.create_messages_for_mailing(self.mailing_id, clients):
            logger.error("Не получилось добавить сообщения в базу")

        with Postgresql() as connection:
            cursor = connection.cursor()
            for client in clients:
                if not MailingService.compare_time(self.end_time):
                    message_id = MessagesRepository.get_message_id_by_client_id_with_cursor(cursor, client[0], self.mailing_id)

                    request_body = {
                        "id": message_id,
                        "phone": int(client[1]),
                        "text": str(self.message)
                    }

                    response = requests.post(
                        url=f"{config.API_URL}/send/{message_id}",
                        headers=self.headers,
                        data=json.dumps(request_body)
                    )
                    if response.status_code != 200:
                        logger.warning(f"Status code ответа: {response.status_code}")
                        MessagesRepository.update_status_with_cursor(cursor, message_id, "failed")
                        connection.commit()
                        continue

                    response = json.loads(response.text)

                    if response["message"] != "OK":
                        MessagesRepository.update_status_with_cursor(cursor, message_id, "failed")
                        logger.warning(f"Сообщение не дошло до пользователя, ответ от удаленного API: {response}")
                    elif response["message"] == "OK":
                        MessagesRepository.update_status_with_cursor(cursor, message_id, "successfully sent")
                        logger.debug("Сообщение дошло")

                    connection.commit()
                else:
                    logger.warning("Время на отправку сообщений закончилось, не все сообщения успели доставиться")
                    break


class StatsService:
    @staticmethod
    def get_messages_statuses_count(messages: list) -> tuple:
        success_message_count = int()
        failed_message_count = int()
        pending_message_count = int()
        for message in messages:
            if message[2] == "failed":
                failed_message_count += 1
            elif message[2] == "successfully sent":
                success_message_count += 1
            elif message[2] == "pending":
                pending_message_count += 1

        return failed_message_count, success_message_count, pending_message_count

    @staticmethod
    def get_base_stats(mailings: list) -> dict:
        base_stats = dict()
        base_stats["mailings_count"] = len(mailings)
        base_stats["mailings"] = dict()

        for mailing in mailings:
            base_stats["mailings"][mailing[0]] = dict()
            messages = MessagesRepository.get_mailing_messages(mailing[0])

            base_stats["mailings"][mailing[0]]["mailing_data"] = Mailing(
                    start_time=mailing[1],
                    message=mailing[2],
                    filters=mailing[3],
                    end_time=mailing[4]
                )

            failed_message_count, success_message_count, pending_message_count = \
                StatsService.get_messages_statuses_count(messages)

            base_stats["mailings"][mailing[0]]["messages_count"] = len(messages)
            base_stats["mailings"][mailing[0]]["success_message_count"] = success_message_count
            base_stats["mailings"][mailing[0]]["failed_message_count"] = failed_message_count
            base_stats["mailings"][mailing[0]]["pending_message_count"] = pending_message_count

        return base_stats

    @staticmethod
    def get_stats_for_mailing(mailing_id: int, messages: list):
        stats_for_mailing = dict({"stats": {mailing_id: dict()}})
        failed_message_count, success_message_count, pending_message_count = \
            StatsService.get_messages_statuses_count(messages)

        stats_for_mailing["stats"][mailing_id]["failed_message_count"] = failed_message_count
        stats_for_mailing["stats"][mailing_id]["success_message_count"] = success_message_count
        stats_for_mailing["stats"][mailing_id]["pending_message_count"] = pending_message_count

        for message in messages:
            stats_for_mailing["stats"][mailing_id][message[0]] = Message(
                    creation_time=message[1],
                    status=message[2],
                    mailing_id=message[3],
                    client_id=message[4]
                )

        return stats_for_mailing
