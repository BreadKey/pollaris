import json


def getData(event) -> dict:
    return event.get("queryStringParameters") or json.loads(event.get("body") or "{}")
