import json
from typing import Any


def getData(event) -> dict:
    return event.get("queryStringParameters") or __parseBody(event.get("body"))

def __parseBody(body: Any) -> dict:
    if isinstance(body, dict):
        return body
    else: return json.loads(body or "{}")