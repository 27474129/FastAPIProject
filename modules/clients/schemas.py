from pydantic import BaseModel


class Client(BaseModel):
    phone: int
    operator_code: int
    tag: str
    time_zone: str
