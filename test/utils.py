import sys
from io import StringIO


def withTestUser(test):
    def wrapper(*args, **kwargs):
        __createTsstUser()
        test(*args, **kwargs)

    return wrapper


def __createTsstUser():
    from auth import model, repository

    user = model.User("breadkey", "이영기입니다", True, [
        model.Role.Admin, model.Role.User])

    repository.createUser(user, "secret")


class Capturing(list):
    def __enter__(self):
        self._stdout = sys.stdout
        sys.stdout = self._stringio = StringIO()
        return self

    def __exit__(self, *args):
        self.extend(self._stringio.getvalue().splitlines())
        del self._stringio    # free up some memory
        sys.stdout = self._stdout
