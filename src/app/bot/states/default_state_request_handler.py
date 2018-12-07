from app.bot.mvc import RequestContainer
from app.bot.reqhandler import RequestHandlerState, StateChanger


class DefaultRequestHandlerState(RequestHandlerState):
    def handle(self, state_changer: StateChanger, request_container: RequestContainer):
        # Do nothing
        # Everything useful is in AnyStateRequestHandler
        pass
