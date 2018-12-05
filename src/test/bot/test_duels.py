from typing import Optional
from unittest.mock import Mock

from app.bot import templates
from app.bot.notification_service import NotificationService
from app.core import Game, Language, GameOutcome, RatingSystem
from app.core.checksys import CheckingSystem, GameVerdict, GameOutcomeReason
from app.model import SourceCode, Solution
from test.bot import AppTestCase


class ManualCheckingSystem(CheckingSystem):
    def __init__(self):
        self.outcome = GameOutcome.FIRST_WIN

    def evaluate(self, game: Game, id1: str, source1: SourceCode, id2: str, source2: SourceCode) -> GameVerdict:
        return GameVerdict(self.outcome, GameOutcomeReason.OK)


class TestRatingSystem(RatingSystem):
    def update_rating(self, rating_1: Optional[int], rating_2: Optional[int], outcome: GameOutcome) -> (int, int):
        rating_1 = rating_1 or 0
        rating_2 = rating_2 or 0

        if outcome == GameOutcome.FIRST_WIN:
            rating_1 += 2
            rating_2 -= 2
        elif outcome == GameOutcome.SECOND_WIN:
            rating_1 -= 2
            rating_2 += 2
        else:
            rating_1 -= 1
            rating_2 += 1

        return rating_1, rating_2


class TestGameSolutions(AppTestCase):
    def setUp(self) -> None:
        self.g1 = Game('g1', 'Game 1')
        self.l1 = Language('l1', 'Lang 1')
        self.csys = ManualCheckingSystem()
        self.notification_service = Mock(spec=NotificationService)
        self.set_up_app(games=[self.g1], languages=[self.l1], check_sys=self.csys,
                        rating_system=TestRatingSystem(), notification_service=self.notification_service)

        # Upload solutions
        s = SourceCode('a.py', b'print()', self.l1.name)
        self.components.solutions_dao.create_solution(1, self.g1.name, s)
        self.components.solutions_dao.create_solution(2, self.g1.name, s)

    def tearDown(self) -> None:
        self.tear_down_app()

    def test_duels_affect_rating(self):
        # Determine duel commands
        s1_cmd = self.components.solutions_dao.find_solution(1, self.g1.name).create_link().to_command()
        s2_cmd = self.components.solutions_dao.find_solution(2, self.g1.name).create_link().to_command()
        # Duel! 1 duels with 2 and wins
        self.csys.outcome = GameOutcome.FIRST_WIN
        self.assert_has_answer(s2_cmd, templates.duel_started, user_id=1)
        sol1: Solution = self.components.solutions_dao.find_solution(1, self.g1.name)
        sol2: Solution = self.components.solutions_dao.find_solution(2, self.g1.name)
        self.assertEqual(sol1.rating, 2)
        self.assertEqual(sol2.rating, -2)
        # Duel! 2 duels with 1 and loses
        self.csys.outcome = GameOutcome.SECOND_WIN
        self.assert_has_answer(s1_cmd, templates.duel_started, user_id=2)
        sol1: Solution = self.components.solutions_dao.find_solution(1, self.g1.name)
        sol2: Solution = self.components.solutions_dao.find_solution(2, self.g1.name)
        self.assertEqual(sol1.rating, 4)
        self.assertEqual(sol2.rating, -4)
        # Duel! 2 duels with 1 and tie
        self.csys.outcome = GameOutcome.TIE
        self.assert_has_answer(s1_cmd, templates.duel_started, user_id=2)
        sol1: Solution = self.components.solutions_dao.find_solution(1, self.g1.name)
        sol2: Solution = self.components.solutions_dao.find_solution(2, self.g1.name)
        self.assertEqual(sol1.rating, 5)
        self.assertEqual(sol2.rating, -5)

    def test_duels_with_self_do_not_affect_rating(self):
        s1_cmd = self.components.solutions_dao.find_solution(1, self.g1.name).create_link().to_command()
        self.csys.outcome = GameOutcome.FIRST_WIN
        self.assert_has_answer(s1_cmd, templates.duel_started, user_id=1)
        sol1: Solution = self.components.solutions_dao.find_solution(1, self.g1.name)
        self.assertIsNone(sol1.rating)

    def test_duels_send_notifications(self):
        # Determine duel commands
        s1_cmd = self.components.solutions_dao.find_solution(1, self.g1.name).create_link().to_command()
        # Duel! 1 duels with 2 and wins
        self.csys.outcome = GameOutcome.FIRST_WIN
        self.assert_has_answer(s1_cmd, templates.duel_started, user_id=2)
        # Check notifications
        self.assert_duel_notifications_are_valid()

        # The same again: check formatting when ratings are set before duel
        self.csys.outcome = GameOutcome.SECOND_WIN
        self.assert_has_answer(s1_cmd, templates.duel_started, user_id=2)
        self.assert_duel_notifications_are_valid()

        # And with TIE
        self.csys.outcome = GameOutcome.TIE
        self.assert_has_answer(s1_cmd, templates.duel_started, user_id=2)
        self.assert_duel_notifications_are_valid()

    def assert_duel_notifications_are_valid(self, num_notifications: int = 2):
        calls = list(self.notification_service.notify_user.mock_calls)
        self.assertEqual(len(calls), num_notifications)
        notified_users = []
        for call in calls:
            _, (user_id, template, args), _ = call
            notified_users.append(user_id)
            # Check template validity
            template.create_message(args)
        self.assertEqual(set(notified_users), set(range(1, num_notifications + 1)))

        # Reset calls
        self.notification_service.notify_user.reset_mock()

    def test_duels_with_self_send_one_notification(self):
        # Determine duel commands
        s1_cmd = self.components.solutions_dao.find_solution(1, self.g1.name).create_link().to_command()
        # Duel! 1 duels with 2 and wins
        self.csys.outcome = GameOutcome.FIRST_WIN
        self.assert_has_answer(s1_cmd, templates.duel_started, user_id=1)
        # Check notifications
        self.assert_duel_notifications_are_valid(num_notifications=1)
