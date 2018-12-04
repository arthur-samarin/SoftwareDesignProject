from unittest import TestCase

from app.bot.mvc import Template, RequestContainer, ResponseReplyTemplate, RequestHandler, Request
from app.bot.reqhandler import ExceptionHandlingRequestHandler, BotException
from test.bot import RequestFaker

exception_template = Template.constant_html('You are not allowed to do {X}!')


class ExceptionThrowingRequestHandler(RequestHandler):

    def handle(self, container: RequestContainer) -> None:
        if container.request.has_text('bot'):
            raise BotException(exception_template, {'X': 'Y'})
        else:
            raise Exception('Some internal exception')


class TestExceptionHandlingRequestHandler(TestCase):
    def setUp(self):
        def internal_exception_handler(_: Request, exception_info: tuple):
            self.last_exception_info = exception_info

        self.last_exception_info = None
        self.rh = ExceptionHandlingRequestHandler(ExceptionThrowingRequestHandler(), internal_exception_handler)

    def test_bot_exception(self):
        self.assert_has_answer('bot', exception_template, {'X': 'Y'})

    def test_internal_exception(self):
        self.assert_no_answer('.')
        self.assertIsNotNone(self.last_exception_info)
        self.assertEqual(('Some internal exception',), self.last_exception_info[1].args)

    def assert_has_answer(self, message_text: str, template: Template, args: dict):
        request = RequestFaker.message(message_text)
        container = RequestContainer(request)

        self.rh.handle(container)

        self.assertEqual(1, len(container.responses))
        response = container.responses[0]
        self.assertIsInstance(response, ResponseReplyTemplate)
        self.assertEqual(template, response.template)
        self.assertEqual(args, response.args)

    def assert_no_answer(self, message_text: str):
        request = RequestFaker.message(message_text)
        container = RequestContainer(request)
        self.rh.handle(container)
        self.assertEqual(0, len(container.responses))
