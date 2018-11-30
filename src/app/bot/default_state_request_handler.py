import app.bot.buttons as buttons
import app.bot.templates as templates
from app.bot.mvc import RequestContainer
from app.bot.reqhandler import RequestHandlerState, StateChanger


class DefaultRequestHandlerState(RequestHandlerState):
    def handle(self, state_changer: StateChanger, request_container: RequestContainer):
        if request_container.request.is_command('start'):
            request_container.add_template_reply(templates.start_message)
        elif request_container.request.has_text(buttons.button_about):
            request_container.add_template_reply(templates.about_bot)
