from datetime import datetime
from test import db
from test.utils import withTestUser
from unittest import TestCase, main


class PollServiceTest(TestCase):
    def setUp(self) -> None:
        db.setUp()

    def tearDown(self) -> None:
        db.tearDown()

    def testAnswerToNotExistPoll(self):
        from poll import service
        from poll.model import Answer, Option
        from poll.error import PollNotExistError

        with self.assertRaises(PollNotExistError):
            service.answer(Answer("breadkey", Option(
                0, 0, "", None), datetime.utcnow()))

    @withTestUser
    def testAnswerTwice(self):
        from poll import service
        from poll.model import Poll, Answer, Option
        from poll.error import AlreadyAnsweredError

        createdPoll = service.createPoll(
            Poll("breadkey", "hello", [
                 Option(None, 0, "world", None), Option(None, 1, "bye", None)])
        )

        service.answer(
            Answer("breadkey", createdPoll.options[0], datetime.utcnow()))

        with self.assertRaises(AlreadyAnsweredError):
            service.answer(
                Answer("breadkey", createdPoll.options[1], datetime.utcnow()))

    @withTestUser
    def testPage(self):
        from poll import service
        from poll.model import Poll, Answer, Option

        poll = service.createPoll(Poll("breadkey", "hello", [Option(
            None, 0, "world", None), Option(None, 1, "world", None)]))

        service.answer(Answer("breadkey", poll.options[0]))

        polls = service.page(None, 10, "breadkey")

        self.assertEqual(polls[0].userAnswerAt, 0)


if (__name__ == '__main__'):
    main()
