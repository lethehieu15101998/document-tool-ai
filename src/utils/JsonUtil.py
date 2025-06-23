import json
import re

from pydantic import BaseModel


class DiagramDescriptions(BaseModel):
    relationshipDiagramDescription: str
    functionDiagramDescription: str


def parse_diagram(response: str) -> DiagramDescriptions | None:
    match = re.search(r"```json\s*([\s\S]*?)\s*```", response)
    if not match:
        return None
    try:
        return DiagramDescriptions(**json.loads(match.group(1)))
    except:
        return None
