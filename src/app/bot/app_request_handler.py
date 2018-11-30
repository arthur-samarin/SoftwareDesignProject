import logging

from app.bot.mvc import RequestHandler, RequestContainer, Request
from app.bot.reqhandler import StateBasedRequestHandler, ExceptionHandlingRequestHandler
from app.bot.states import DefaultRequestHandlerState
from app.core import GamesRegistry
from app.dao import Database
from app.dao.solutions_dao import SolutionsDao

logger = logging.getLogger(__name__)


class AppRequestHandler(RequestHandler):
    def __init__(self, games_registry: GamesRegistry = None, db: Database = None, solutions_dao: SolutionsDao = None):
        state_based_handler = StateBasedRequestHandler(
            key_extractor=StateBasedRequestHandler.chat_id_key_extractor,
            default_state=DefaultRequestHandlerState(games_registry, db, solutions_dao)
        )
        self._wrapped = ExceptionHandlingRequestHandler(state_based_handler, self.__handle_internal_exception)

    def handle(self, container: RequestContainer) -> None:
        self._wrapped.handle(container)

    @staticmethod
    def __handle_internal_exception(request: Request, exc_info: tuple):
        logger.warning('Exception handling request #%d', request.update.update_id, exc_info=exc_info)
