import json


def getData(event) -> dict:
    return event.get("queryStringParameters", json.loads(event.get("body", "{}") or "{}")) or {}
