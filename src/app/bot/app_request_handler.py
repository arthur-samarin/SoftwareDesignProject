import logging

from app import Components
from app.bot.mvc import RequestHandler, RequestContainer, Request
from app.bot.reqhandler import StateBasedRequestHandler, ExceptionHandlingRequestHandler
from app.bot.states import DefaultRequestHandlerState

logger = logging.getLogger(__name__)


class AppRequestHandler(RequestHandler):
    def __init__(self, components: Components):
        state_based_handler = StateBasedRequestHandler(
            key_extractor=StateBasedRequestHandler.chat_id_key_extractor,
            default_state=DefaultRequestHandlerState(components)
        )
        self._wrapped = ExceptionHandlingRequestHandler(state_based_handler, self.__handle_internal_exception)

    def handle(self, container: RequestContainer) -> None:
        self._wrapped.handle(container)

    @staticmethod
    def __handle_internal_exception(request: Request, exc_info: tuple):
        logger.warning('Exception handling request #%d', request.update.update_id, exc_info=exc_info)
