from pydantic import BaseModel

class Notification(BaseModel):
    event_type : str
    data: dict