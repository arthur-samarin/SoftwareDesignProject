from unittest import TestCase

from concurrent.futures.thread import ThreadPoolExecutor
from typing import List, Union

from app.bot import Components, AppRequestHandler
from app.bot.mvc import Template, RequestContainer, ResponseReplyTemplate, FileHandle
from app.bot.notification_service import NotificationService
from app.core import Game, GamesRegistry, Language, LanguageRegistry, RatingSystem
from app.core.checksys import CheckingSystem
from app.core.checksys.async_checking_system import SyncCheckingSystem
from app.dao.solutions_dao import SolutionsDao
from test.bot import RequestFaker
from test.dao import DatabaseTestHelper


class AppTestCase(TestCase):
    def set_up_app(self, games: List[Game] = None, languages: List[Language] = None, check_sys: CheckingSystem = None,
                   rating_system: RatingSystem = None, notification_service: NotificationService = None) -> None:
        self.dth = DatabaseTestHelper()
        self.dth.set_up()
        self.thread_pool = ThreadPoolExecutor(2)

        self.components = Components(
            database=self.dth.db,
            solutions_dao=SolutionsDao(self.dth.db),
            games_registry=GamesRegistry.from_games(games or []),
            languages_registry=LanguageRegistry.from_languages(languages or []),
            checking_system=(SyncCheckingSystem(check_sys) if check_sys else None),
            rating_system=rating_system,
            notification_service=notification_service
        )
        self.rh = AppRequestHandler(self.components)

    def tear_down_app(self) -> None:
        self.dth.tear_down()
        self.thread_pool.shutdown()

    def assert_has_answer(self, message_content: Union[FileHandle, str], template: Template, user_id: int = 42) -> dict:
        request = RequestFaker.message(message_content, user_id=user_id)
        container = RequestContainer(request)

        self.rh.handle(container)

        self.assertEqual(1, len(container.responses))
        response = container.responses[0]
        self.assertIsInstance(response, ResponseReplyTemplate)
        self.assertEqual(template, response.template)

        # Test that message can be constructed without errors
        response.get_content()

        return response.args

    def assert_has_answers(self, message_content: Union[FileHandle, str], template_1: Template, template_2: Template) -> dict:
        request = RequestFaker.message(message_content)
        container = RequestContainer(request)

        self.rh.handle(container)

        self.assertEqual(2, len(container.responses))
        response1 = container.responses[0]
        self.assertIsInstance(response1, ResponseReplyTemplate)
        self.assertEqual(template_1, response1.template)
        response1.get_content()
        response2 = container.responses[1]
        self.assertIsInstance(response2, ResponseReplyTemplate)
        self.assertEqual(template_2, response2.template)
        response2.get_content()

        return container.responses[1].args
