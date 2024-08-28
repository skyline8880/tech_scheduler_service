import datetime as dt

from pydantic import BaseModel


class Request(BaseModel):
    token: str
    department_id: int
    deal_id: int
    start_date: dt.datetime
