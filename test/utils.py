def withTestUser(test):
    def wrapper(*args, **kwargs):
        __createTsstUser()
        test(*args, **kwargs)

    return wrapper

def __createTsstUser():
    from auth import repository, model

    user = model.User("breadkey", "testBK", True, [
                        model.Role.Admin, model.Role.User])

    repository.createUser(user, "secret")