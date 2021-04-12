import json


def getData(event):
    return event.get("queryStringParameters", json.loads(event.get("body", "{}") or "{}")) or {}
