from pydantic import BaseModel, validator
from datetime import datetime


class Mailing(BaseModel):
    start_time: datetime
    message: str
    filters: str = None
    end_time: datetime

    # валидирование корректности фильтра
    @validator("filters")
    def validate_filters(cls, filters: str or None):
        if filters != "None":
            if "=" not in filters:
                raise ValueError("Некорректный фильтр")

            splited_filters = filters.split("=")
            if splited_filters[0] != "tag" and splited_filters[0] != "timezone":
                raise ValueError("Некорректный фильтр")
        return filters


class Message(BaseModel):
    creation_time: datetime
    status: str
    mailing_id: int
    client_id: int
