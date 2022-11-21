import logging
from modules.context_managers import Postgresql
from .schemas import Client


logger = logging.getLogger(__name__)


class ClientsRepository:
    @staticmethod
    def create_client(client_data: Client) -> int:
        with Postgresql() as connection:
            cursor = connection.cursor()
            cursor.execute(f"INSERT INTO clients (phone, operator_code, tag, time_zone)\
             VALUES ({client_data.phone}, {client_data.operator_code}, \
             '{client_data.tag}', '{client_data.time_zone}') RETURNING id;")
            client_id = cursor.fetchall()[0][0]
            logger.debug(f"Клиент создан, его id: {client_id}")
            return client_id

    @staticmethod
    def delete_client(client_id: int) -> bool:
        with Postgresql() as connection:
            cursor = connection.cursor()
            cursor.execute(f"DELETE FROM clients WHERE id={client_id};")
            logger.debug(f"Клиент удален, его id: {client_id}")
        return True

    @staticmethod
    def update_client(client_id: int, client_data: Client) -> bool:
        with Postgresql() as connection:
            cursor = connection.cursor()
            cursor.execute(f"UPDATE clients SET phone={client_data.phone}, \
            operator_code={client_data.operator_code}, tag='{client_data.tag}',\
             time_zone='{client_data.time_zone}' WHERE id={client_id};")
            logger.debug(f"Клиент обновлен, его id: {client_id}")
        return True

    @staticmethod
    def get_client_by_id(client_id: int) -> Client or None:
        with Postgresql() as connection:
            cursor = connection.cursor()
            cursor.execute(f"SELECT * FROM clients WHERE id={client_id};")
            client_data = cursor.fetchall()
            if len(client_data) == 1:
                client_data = client_data[0]
            else:
                return None
            client = Client(
                phone=client_data[1],
                operator_code=client_data[2],
                tag=client_data[3],
                time_zone=client_data[4]
            )
            logger.debug(f"Клиент получен, его id: {client_id}")
            return client

    @staticmethod
    def get_clients(filters: list or str):
        with Postgresql() as connection:
            cursor = connection.cursor()
            if filters == "None":
                cursor.execute(f"SELECT * FROM clients;")
            else:
                cursor.execute(f"SELECT * FROM clients WHERE {filters[0]}='{filters[1]}';")
            return cursor.fetchall()
