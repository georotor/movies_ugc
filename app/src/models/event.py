from pydantic import BaseModel


class Event(BaseModel):
    topic: str
    key: str
    value: str
