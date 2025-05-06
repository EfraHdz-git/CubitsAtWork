# app/api/models/request_models.py
from pydantic import BaseModel

class TextInputRequest(BaseModel):
    text: str