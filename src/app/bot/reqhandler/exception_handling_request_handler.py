import logging
import sys
from typing import Callable

from app.bot.mvc import RequestHandler, RequestContainer, Request
from app.bot.reqhandler import BotException

logger = logging.getLogger(__name__)


class ExceptionHandlingRequestHandler(RequestHandler):
    def __init__(self, wrapped: RequestHandler, internal_exception_handler: Callable[[Request, tuple], None]):
        self.wrapped = wrapped
        self.internal_exception_handler = internal_exception_handler

    def handle(self, container: RequestContainer) -> None:
        try:
            self.wrapped.handle(container)
        except BotException as ex:
            container.stop_handling()
            self.__handle_bot_exception(container, ex)
        except Exception:
            self.__handle_exception(container)

    @staticmethod
    def __handle_bot_exception(container: RequestContainer, ex: BotException):
        response = ex.to_response()
        container.responses.append(response)

    def __handle_exception(self, container: RequestContainer):
        self.internal_exception_handler(container.request, sys.exc_info())
