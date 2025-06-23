# app/models/file_model.py
from pydantic import BaseModel


class UploadResult(BaseModel):
    filename: str
