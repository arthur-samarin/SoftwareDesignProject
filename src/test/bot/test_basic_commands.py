from unittest import TestCase

from app.bot import AppRequestHandler, templates, buttons
from app.bot.mvc import Template, RequestContainer, ResponseReplyTemplate
from test.bot import RequestFaker


class TestBasicCommands(TestCase):
    def setUp(self):
        self.rh = AppRequestHandler()

    def test_start(self):
        self.assert_has_answer('/start', templates.start_message)

    def test_about(self):
        self.assert_has_answer(buttons.button_about, templates.about_bot)

    def assert_has_answer(self, message_text: str, template: Template):
        request = RequestFaker.text_message(message_text)
        container = RequestContainer(request)

        self.rh.handle(container)

        self.assertEqual(1, len(container.responses))
        response = container.responses[0]
        self.assertIsInstance(response, ResponseReplyTemplate)
        self.assertEqual(template, response.template)
