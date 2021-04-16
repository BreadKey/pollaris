from handler import response


def needData(request):
    def wrapper(*args, **kwargs):
        try:
            return request(*args, **kwargs)
        except KeyError as key:
            return response.badRequest(f'{key} not found')

    return wrapper