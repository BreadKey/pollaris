from test import db
from test.utils import withTestUser

from unittest import TestCase, main


class RepositoryTest(TestCase):
    def setUp(self):
        db.setUp()

    def tearDown(self):
        db.tearDown()

    @withTestUser
    def testSaveUser(self):
        from auth import repository, model
        foundUser = repository.findUserById("breadkey")

        self.assertEqual(foundUser.nickname, "이영기입니다")
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


if (__name__ == '__main__'):
    main()
