from pydantic import BaseModel
from datetime import datetime


class Mailing(BaseModel):
    start_time: datetime
    message: str
    filters: str
    end_time: datetime


class Message(BaseModel):
    creation_time: datetime
    status: str
    mailing_id: int
    client_id: int
