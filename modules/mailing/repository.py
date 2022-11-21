import logging
from modules.context_managers import Postgresql
from .schemas import Mailing
from datetime import datetime
from pytz import timezone


logger = logging.getLogger(__name__)


class MailingRepository:
    @staticmethod
    def create_mailing(mailing_data: Mailing) -> int:
        with Postgresql() as connection:
            cursor = connection.cursor()
            cursor.execute(f"INSERT INTO mailings (start_time, message, filters, end_time)\
             VALUES ('{mailing_data.start_time}', '{mailing_data.message}', \
            '{mailing_data.filters}', '{mailing_data.end_time}') RETURNING id;")
            mailing_id = cursor.fetchall()[0][0]
            logger.debug(f"Новая рассылка создана, ее id: {mailing_id}")
            return mailing_id

    @staticmethod
    def get_mailing_by_id(mailing_id: int) -> Mailing or None:
        with Postgresql() as connection:
            cursor = connection.cursor()
            cursor.execute(f"SELECT * FROM mailings WHERE id={mailing_id};")
            mailing_data = cursor.fetchall()
            if len(mailing_data) == 1:
                mailing_data = mailing_data[0]
            else:
                return None

            mailing = Mailing(
                start_time=mailing_data[1],
                message=mailing_data[2],
                filters=mailing_data[3],
                end_time=mailing_data[4]
            )
            logger.debug(f"Рассылка получена, ее id: {mailing_id}")
            return mailing

    @staticmethod
    def delete_mailing(mailing_id: int) -> bool:
        with Postgresql() as connection:
            cursor = connection.cursor()
            cursor.execute(f"DELETE FROM mailings WHERE id={mailing_id};")
        logger.debug(f"Рассылка удалена, ее id: {mailing_id}")
        return True

    @staticmethod
    def update_mailing(mailing_data: Mailing) -> bool:
        with Postgresql() as connection:
            cursor = connection.cursor()
            cursor.execute(f"UPDATE mailings SET start_time='{mailing_data.start_time}', \
            message='{mailing_data.message}', filters='{mailing_data.filters}', end_time='{mailing_data.end_time}';")
            logger.debug("Рассылка обновлена")
        return True

    @staticmethod
    def get_all_mailings() -> list:
        with Postgresql() as connection:
            cursor = connection.cursor()
            cursor.execute(f"SELECT * FROM mailings;")
            return cursor.fetchall()


class MessagesRepository:
    @staticmethod
    def create_messages_for_mailing(mailing_id: int, clients: list) -> bool:
        # создание сообщений для рассылки через транзакцию
        with Postgresql() as connection:
            cursor = connection.cursor()
            for client in clients:
                cursor.execute(f"INSERT INTO messages (creation_time, status, mailing_id, client_id)\
                     VALUES ('{datetime.now(tz=timezone('Europe/Moscow'))}',\
                      'pending', {mailing_id}, {client[0]}) RETURNING id;")
                logger.debug(f"Сообщение создано, id рассылки: {mailing_id} id клиента: {client[0]}")
        return True

    @staticmethod
    def get_message_id_by_client_id_with_cursor(cursor, client_id: int, mailing_id: int) -> int:
        cursor.execute(f"SELECT id FROM messages WHERE client_id={client_id} AND mailing_id={mailing_id};")
        message = cursor.fetchall()
        return message[0][0] if len(message) == 1 else None

    @staticmethod
    def update_status_with_cursor(cursor, message_id: int, new_status: str) -> bool:
        cursor.execute(f"UPDATE messages SET status='{new_status}' WHERE id={message_id};")
        return True

    @staticmethod
    def get_mailing_messages(mailing_id: int) -> list:
        with Postgresql() as connection:
            cursor = connection.cursor()
            cursor.execute(f"SELECT * FROM messages WHERE mailing_id={mailing_id};")
            return cursor.fetchall()
