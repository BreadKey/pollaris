def ok(body: str = None): return __response(200, body)
def created(body: str = None): return __response(201, body)
def badRequest(body: str = None): return __response(400, body)
def conflict(body: str = None): return __response(409, body)


def __response(statusCode: int, body: str = None): return {
    "statusCode": statusCode,
    "body":  body
}
