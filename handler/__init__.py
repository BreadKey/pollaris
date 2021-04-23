from handler import response, request


def needData(request):
    def wrapper(event, context):
        try:
            return request(event, context)
        except KeyError as key:
            return response.badRequest(f'{key} not found')

    return wrapper

def private(_request):
    def wrapper(event, context):
        try:
            data = request.getData(event)
            userId = data["userId"]
            authorizedUserId = event["requestContext"]["authorizer"]["principalId"]
            assert userId == authorizedUserId
            return _request(event, context)
        except:
            return response.unauthorized()

    return wrapper