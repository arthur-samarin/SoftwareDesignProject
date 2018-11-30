import logging

from app.bot import DefaultRequestHandlerState
from app.bot.mvc import RequestHandler, RequestContainer, Request
from app.bot.reqhandler import StateBasedRequestHandler, ExceptionHandlingRequestHandler

logger = logging.getLogger(__name__)


class AppRequestHandler(RequestHandler):
    def __init__(self):
        state_based_handler = StateBasedRequestHandler(
            key_extractor=StateBasedRequestHandler.chat_id_key_extractor,
            default_state=DefaultRequestHandlerState()
        )
        self._wrapped = ExceptionHandlingRequestHandler(state_based_handler, self.__handle_internal_exception)

    def handle(self, container: RequestContainer) -> None:
        self._wrapped.handle(container)

    @staticmethod
    def __handle_internal_exception(request: Request, exc_info: tuple):
        logger.warning('Exception handling request #%d', request.update.update_id, exc_info=exc_info)
