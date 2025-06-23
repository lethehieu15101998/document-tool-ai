import os

from fastapi import UploadFile

from src.config.config import QUESTIONS_DIR


async def save_file_to_questions(file: UploadFile) -> str:
    os.makedirs(QUESTIONS_DIR, exist_ok=True)
    file_name = file.filename
    content = await file.read()
    file_path = os.path.join(QUESTIONS_DIR, file_name)
    with open(file_path, "wb") as f:
        f.write(content)
    return file_name
