import json
import re
from typing import Optional, Type, TypeVar

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


def parse_diagram(response: str, model: Type[T]) -> Optional[T]:
    match = re.search(r"```json\s*([\s\S]*?)\s*```", response)
    if not match:
        return None
    raw_json = match.group(1)

    # Làm sạch chuỗi JSON lỗi
    cleaned = raw_json.replace("\x00", "")  # null byte
    cleaned = re.sub(r"[\x00-\x1F]+", "", cleaned)  # ký tự điều khiển
    try:
        data = json.loads(cleaned)
        return model(**data)
    except Exception as e:
        print("❌ Parse failed:", e)
        return None
