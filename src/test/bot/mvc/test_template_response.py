from unittest import TestCase
from unittest.mock import Mock

from telegram import Bot, ReplyKeyboardMarkup

from app.bot.mvc import ResponseReplyTemplate, Template, MessageContent
from test.bot import RequestFaker


class TestTemplateResponse(TestCase):
    def test_without_buttons(self):
        text = 'Hello, world!'
        template = Template.constant(MessageContent(text=text))

        bot_mock = Mock(spec=Bot)
        request = RequestFaker.text_message()
        ResponseReplyTemplate(template).send(bot_mock, request)

        bot_mock.send_message.assert_called_once()
        call_args = bot_mock.send_message.call_args
        args, kwargs = call_args

        self.assertEqual(args, (request.update.message.from_user.id, text))
        self.assertIsNone(kwargs.get('reply_markup'))
        self.assertEqual(kwargs['parse_mode'], 'html')

    def test_with_buttons(self):
        text = 'Hello, world!'
        template = Template.constant(MessageContent(text=text, buttons=[
            ['A', 'B'], ['C', 'D', 'E']
        ]))

        bot_mock = Mock(spec=Bot)
        request = RequestFaker.text_message()
        ResponseReplyTemplate(template).send(bot_mock, request)

        bot_mock.send_message.assert_called_once()
        call_args = bot_mock.send_message.call_args
        args, kwargs = call_args

        self.assertEqual(args, (request.update.message.from_user.id, text))
        self.assertIsInstance(kwargs['reply_markup'], ReplyKeyboardMarkup)
        self.assertEqual(kwargs['reply_markup'].keyboard, [['A', 'B'], ['C', 'D', 'E']])
        self.assertEqual(kwargs['parse_mode'], 'html')
