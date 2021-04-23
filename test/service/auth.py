import base64
import json
from datetime import datetime, timedelta
from test import db
from test.utils import withTestUser
from unittest import TestCase, main

import jwt


class AuthServiceTest(TestCase):
    def setUp(self) -> None:
        db.setUp()

    def tearDown(self) -> None:
        db.tearDown()

    @withTestUser
    def testAuthorizeWithIdentity(self):
        from auth import service
        from auth.error import InvalidAuthError, ExpiredAuthError
        from auth.model import IdentifyMethod, Identity

        identityKey = "fingerprint"

        service.registerIdentity(
            Identity("breadkey", IdentifyMethod.Fingerprint, identityKey))

        challenge = service.requestIdentityChallenge("breadkey")

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

        challenge = service.requestIdentityChallenge("breadkey")

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
