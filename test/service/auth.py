import base64
import json
from test import db
from test.utils import Capturing, withTestUser
from unittest import TestCase, main

from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA

class AuthServiceTest(TestCase):
    def setUp(self) -> None:
        db.setUp()

    def tearDown(self) -> None:
        db.tearDown()

    def testVerify(self):
        from auth import service
        from auth.error import NotVerifiedError
        from auth.model import Role, User
        from auth.error import NotGrantedError

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
        from auth.error import InvalidAuthError
        from auth.model import IdentifyMethod

        encryptKey = self.__generateAndRegisterNewKeyPair()
        challenge = service.getNewIdentityChallenge("breadkey")

        with self.assertRaises(InvalidAuthError):
            service.authorizeWithIdentity("hello")

        content = {
            "userId": "breadkey",
            "challenge": challenge
        }

        rawToken = self.__makeRawToken(content)

        # Test method not match
        content["method"] = IdentifyMethod.Password.name
        with self.assertRaises(InvalidAuthError):
            service.authorizeWithIdentity(rawToken)

        # Test succeed
        content["method"] = IdentifyMethod.Fingerprint.name
        content["challenge"] = self.__encryptChallenge(encryptKey, challenge)

        rawToken = self.__makeRawToken(content)
        self.assertEqual(service.authorizeWithIdentity(rawToken), "breadkey")

        # Test reauthorize with same token
        with self.assertRaises(InvalidAuthError):
            service.authorizeWithIdentity(rawToken)

        # Test sign with old key
        self.__generateAndRegisterNewKeyPair()
        challenge = service.getNewIdentityChallenge("breadkey")

        content["challenge"] = self.__encryptChallenge(encryptKey, challenge)
        rawToken = self.__makeRawToken(content)

        with self.assertRaises(InvalidAuthError):
            service.authorizeWithIdentity(rawToken)

    def __generateAndRegisterNewKeyPair(self):
        from auth import service
        from auth.model import IdentifyMethod
        encryptKey = service.registerIdentity("breadkey", IdentifyMethod.Fingerprint)

        return RSA.importKey(encryptKey.encode('utf-8'))

    def __encryptChallenge(self, key, challenge):
        cipher = PKCS1_OAEP.new(key)
        encryptedChallenge = cipher.encrypt(challenge.encode('utf-8'))
        return base64.encodebytes(encryptedChallenge).decode('utf-8')

    def __makeRawToken(self, content: dict) -> str:
        return base64.b64encode(json.dumps(content).encode('utf-8')).decode('ascii')


if (__name__ == '__main__'):
    main()
