import json


def ok(body=None): return __response(
    200, json.dumps(body) if body else None)


def created(body=None): return __response(
    201, json.dumps(body) if body else None)


def badRequest(message: str = None): return __response(
    400, __buildMessage(message))


def unauthorized(): return __response(401,  __buildMessage("Unauthorized"))


def forbidden(message: str = None): return __response(
    403, __buildMessage(message))


def conflict(message: str = None): return __response(
    409, __buildMessage(message))


def internalServerError(message: str = None): return __response(
    500, __buildMessage(message))


def __response(statusCode: int, body: str = None): return {
    "statusCode": statusCode,
    "body":  body
}


def __buildMessage(
    message: str): return '{"message": "' + message + '"}' if message else None
