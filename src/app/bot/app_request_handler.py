import logging

from app.bot import Components
from app.bot.mvc import RequestHandler, RequestContainer, Request
from app.bot.mvc.request_handler import SequentialRequestHandler
from app.bot.reqhandler import StateBasedRequestHandler, ExceptionHandlingRequestHandler
from app.bot.states import DefaultRequestHandlerState
from app.bot.states.any_state_request_handler import AnyStateRequestHandler

logger = logging.getLogger(__name__)


class AppRequestHandler(RequestHandler):
    def __init__(self, components: Components):
        state_based_handler = StateBasedRequestHandler(
            key_extractor=StateBasedRequestHandler.chat_id_key_extractor,
            default_state=DefaultRequestHandlerState()
        )
        self._wrapped = ExceptionHandlingRequestHandler(SequentialRequestHandler([
            state_based_handler,
            AnyStateRequestHandler(components, state_based_handler)
        ]), self.__handle_internal_exception)

    def handle(self, container: RequestContainer) -> None:
        self._wrapped.handle(container)

    @staticmethod
    def __handle_internal_exception(request: Request, exc_info: tuple):
        logger.warning('Exception handling request #%d', request.update.update_id, exc_info=exc_info)
