from auth.error import NotGrantedError
import base64
import json
from datetime import datetime, timedelta
from test import db
from test.utils import Capturing, withTestUser
from unittest import TestCase, main

import jwt


class AuthServiceTest(TestCase):
    def setUp(self) -> None:
        db.setUp()

    def tearDown(self) -> None:
        db.tearDown()

    def testVerify(self):
        from auth import service
        from auth.model import User, Role
        from auth.error import NotVerifiedError

        user = User("testUser", "testUser", False, [Role.User])

        service.signUp(user, "secret")

        with self.assertRaises(NotVerifiedError):
            auth = service.signIn("testUser", "secret")
            service.authorize(auth, Role.User, needVerification=True)

        with Capturing() as output:
            service.requestVerificationCode("testUser", "+82-1234-5678")

        code = output[0]
        service.verifyIdentity("testUser", code)

        auth = service.signIn("testUser", "secret")
        self.assertEqual(service.authorize(
            auth, Role.User, needVerification=True), "testUser")

        with self.assertRaises(NotGrantedError):
            service.authorize(auth, Role.Admin, needVerification=True)

    @withTestUser
    def testAuthorizeWithIdentity(self):
        from auth import service
        from auth.error import ExpiredAuthError, InvalidAuthError
        from auth.model import IdentifyMethod, Identity

        identityKey = "fingerprint"

        service.registerIdentity(
            Identity("breadkey", IdentifyMethod.Fingerprint, identityKey))

        challenge = service.getNewIdentityChallenge("breadkey")

        with self.assertRaises(InvalidAuthError):
            service.authorizeWithIdentity("hello")

        payload = {
            "challenge": challenge,
            "exp": datetime.utcnow() + timedelta(seconds=30)
        }

        token = jwt.encode(payload, identityKey)

        content = {
            "userId": "breadkey",
            "token": token
        }

        rawToken = self.__makeRawToken(content)

        # Test method not match
        content["method"] = IdentifyMethod.Password.name
        with self.assertRaises(InvalidAuthError):
            service.authorizeWithIdentity(rawToken)

        # Test succeed
        content["method"] = IdentifyMethod.Fingerprint.name
        rawToken = self.__makeRawToken(content)
        self.assertEqual(service.authorizeWithIdentity(rawToken), "breadkey")

        # Test reauthorize with same token
        with self.assertRaises(InvalidAuthError):
            service.authorizeWithIdentity(rawToken)

        # Test sign with old key
        changedKey = "changed key"
        service.registerIdentity(
            Identity("breadkey", IdentifyMethod.Fingerprint, changedKey))

        challenge = service.getNewIdentityChallenge("breadkey")

        payload["challenge"] = challenge
        content["token"] = jwt.encode(payload, identityKey)
        rawToken = self.__makeRawToken(content)

        with self.assertRaises(InvalidAuthError):
            service.authorizeWithIdentity(rawToken)

        # Test expired token
        payload["exp"] = datetime.utcnow() - timedelta(seconds=1)

        token = jwt.encode(payload, changedKey)
        content["token"] = token
        rawToken = self.__makeRawToken(content)

        with self.assertRaises(ExpiredAuthError):
            service.authorizeWithIdentity(rawToken)

    def __makeRawToken(self, content: dict) -> str:
        return base64.b64encode(json.dumps(content).encode('utf-8'))


if (__name__ == '__main__'):
    main()
