import app.bot.buttons as buttons
import app.bot.templates as templates
from app.bot.mvc import RequestContainer
from app.bot.reqhandler import RequestHandlerState, StateChanger
from app.core import Game
from app.dao import Database
from app.dao.solutions_dao import SolutionsDao


class GameChosenState(RequestHandlerState):
    def __init__(self, game: Game, database: Database = None, solutions_dao: SolutionsDao = None):
        self.game = game
        self.database = database
        self.solutions_dao = solutions_dao

    def handle(self, state_changer: StateChanger, request_container: RequestContainer):
        req = request_container.request

        if req.has_text(buttons.button_upload):
            request_container.add_template_reply(templates.upload_solution)
        elif req.has_text(buttons.button_rename):
            request_container.add_template_reply(templates.rename_solution)
        elif req.has_text(buttons.button_change_language):
            request_container.add_template_reply(templates.choose_language)
        elif req.has_text(buttons.button_back):
            # Unknown command: switch to default state
            state_changer.change_and_handle(None, request_container)
