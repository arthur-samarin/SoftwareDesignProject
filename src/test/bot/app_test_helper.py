from unittest import TestCase

from typing import List, Union

from app import Components
from app.bot import AppRequestHandler
from app.bot.mvc import Template, RequestContainer, ResponseReplyTemplate, FileHandle
from app.core import Game, GamesRegistry, Language, LanguageRegistry
from app.dao.solutions_dao import SolutionsDao
from test.bot import RequestFaker
from test.dao import DatabaseTestHelper


class AppTestCase(TestCase):
    def set_up_app(self, games: List[Game] = None, languages: List[Language] = None) -> None:
        self.dth = DatabaseTestHelper()
        self.dth.set_up()

        self.components = Components(
            database=self.dth.db,
            solutions_dao=SolutionsDao(self.dth.db),
            games_registry=GamesRegistry.from_games(games or []),
            languages_registry=LanguageRegistry.from_languages(languages or [])
        )
        self.rh = AppRequestHandler(self.components)

    def tear_down_app(self) -> None:
        self.dth.tear_down()

    def assert_has_answer(self, message_content: Union[FileHandle, str], template: Template) -> dict:
        request = RequestFaker.message(message_content)
        container = RequestContainer(request)

        self.rh.handle(container)

        self.assertEqual(1, len(container.responses))
        response = container.responses[0]
        self.assertIsInstance(response, ResponseReplyTemplate)
        self.assertEqual(template, response.template)

        return response.args

    def assert_has_answers(self, message_content: Union[FileHandle, str], template_1: Template, template_2: Template) -> dict:
        request = RequestFaker.message(message_content)
        container = RequestContainer(request)

        self.rh.handle(container)

        self.assertEqual(2, len(container.responses))
        response = container.responses[0]
        self.assertIsInstance(response, ResponseReplyTemplate)
        self.assertEqual(template_1, response.template)
        response = container.responses[1]
        self.assertIsInstance(response, ResponseReplyTemplate)
        self.assertEqual(template_2, response.template)

        return container.responses[1].args
