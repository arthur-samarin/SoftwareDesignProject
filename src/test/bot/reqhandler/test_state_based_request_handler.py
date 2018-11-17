from unittest import TestCase

from app.bot.mvc import Template, RequestContainer, MessageContent, ResponseReplyTemplate
from app.bot.reqhandler import RequestHandlerState, StateChanger, StateBasedRequestHandler
from test.bot import RequestFaker


class StateA(RequestHandlerState):
    def __init__(self) -> None:
        super().__init__()
        self.counter = 0

    def handle(self, state_changer: StateChanger, request_container: RequestContainer):
        update = request_container.request.update
        message_text = update.message.text if update.message else None

        self.counter += 1
        request_container.add_template_reply(Template.constant(MessageContent('StateA handled this request')), {
            'counter': self.counter
        })

        if message_text == 'SwitchB':
            state_changer.change(StateB())
        elif message_text == 'SwitchDefault':
            state_changer.change(None)

class StateB(RequestHandlerState):
    def handle(self, state_changer: StateChanger, request_container: RequestContainer):
        state_changer.change_and_handle(StateA(), request_container)


class TestStateBasedRequestHandler(TestCase):
    def setUp(self):
        super().setUp()
        self.handler = StateBasedRequestHandler(lambda request: request.effective_chat_id, default_state=StateB())

    def test_one_user(self):
        # Anything increments the counter and returns new value
        # SwitchB or SwitchDefault resets it to 0 (after returning new value)
        self.assertEqual(1, self.handle_and_get_counter(1, 'A'))
        self.assertEqual(2, self.handle_and_get_counter(1, 'A'))
        self.assertEqual(3, self.handle_and_get_counter(1, 'SwitchB'))
        self.assertEqual(1, self.handle_and_get_counter(1, 'A'))
        self.assertEqual(2, self.handle_and_get_counter(1, 'SwitchDefault'))
        self.assertEqual(1, self.handle_and_get_counter(1, 'A'))
        self.assertEqual(2, self.handle_and_get_counter(1, 'A'))
        self.assertEqual(3, self.handle_and_get_counter(1, 'SwitchB'))
        self.assertEqual(1, self.handle_and_get_counter(1, 'A'))
        self.assertEqual(2, self.handle_and_get_counter(1, 'A'))
        self.assertEqual(3, self.handle_and_get_counter(1, 'SwitchB'))
        self.assertEqual(1, self.handle_and_get_counter(1, 'SwitchB'))
        self.assertEqual(1, self.handle_and_get_counter(1, 'A'))

    def test_two_users_are_independent(self):
        self.assertEqual(1, self.handle_and_get_counter(1, 'A'))
        self.assertEqual(1, self.handle_and_get_counter(2, 'A'))
        self.assertEqual(2, self.handle_and_get_counter(1, 'A'))
        self.assertEqual(2, self.handle_and_get_counter(2, 'A'))
        self.assertEqual(3, self.handle_and_get_counter(1, 'SwitchB'))
        self.assertEqual(3, self.handle_and_get_counter(2, 'A'))
        self.assertEqual(4, self.handle_and_get_counter(2, 'A'))

    def handle_and_get_counter(self, user_id, message):
        request = RequestFaker.text_message(message, user_id=user_id)
        request_container = RequestContainer(request)
        self.handler.handle(request_container)

        self.assertEqual(1, len(request_container.responses))
        response = request_container.responses[0]

        self.assertIsInstance(response, ResponseReplyTemplate)
        return response.args['counter']