from test import db

from unittest import TestCase, main


class RepositoryTest(TestCase):
    def setUp(self):
        db.setUp()

    def tearDown(self):
        db.tearDown()

    def withTestUser(test):
        def wrapper(self: 'RepositoryTest'):
            self.__createTestUser()
            test(self)

        return wrapper

    def testSaveUser(self):
        from auth import repository, model

        self.__createTestUser()

        foundUser = repository.findUserById("breadkey")

        self.assertEqual(foundUser.nickname, "testBK")
        self.assertEqual(foundUser.isVerified, True)
        self.assertListEqual(
            foundUser.roles, [model.Role.Admin, model.Role.User])

    @withTestUser
    def testSaveIdentity(self):
        from auth import repository
        from auth.model import IdentifyMethod, Identity

        firstKey = "aksdjfkjn12kj3"
        secondKey = "hello, world?"

        repository.saveIdentity(Identity("breadkey",
                                         IdentifyMethod.Fingerprint, "aksdjfkjn12kj3"))
        self.assertEqual(repository.findIdentityKeyByUserIdAndMethod(
            "breadkey", IdentifyMethod.Fingerprint), firstKey)

        repository.saveIdentity(
            Identity("breadkey", IdentifyMethod.Fingerprint, secondKey))
        self.assertEqual(repository.findIdentityKeyByUserIdAndMethod(
            "breadkey", IdentifyMethod.Fingerprint), secondKey)

    def __createTestUser(self):
        from auth import repository, model

        user = model.User("breadkey", "testBK", True, [
                          model.Role.Admin, model.Role.User])

        repository.createUser(user, "secret")


main()
