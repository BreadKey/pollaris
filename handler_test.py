from test import db as testDb
from unittest import TestCase, main

class HandlerTest(TestCase):
    def setUp( self):
        testDb.setUp()
    def tearDown(self):   
        testDb.tearDown()

    def test_signUp(self):
        from handler import auth
        
        event = {
        "body": {
            "id": "breadkey",
            "nickname": "이영기",
            "roles": ["Admin", "User"]
            }
        }

        self.assertEqual(auth.signUp(event, {})["statusCode"], 400)

        event["body"]["password"] = "secret"

        self.assertEqual(auth.signUp(event, {})["statusCode"], 201)

main()