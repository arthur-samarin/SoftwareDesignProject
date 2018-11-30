import re

import app.bot.buttons as buttons
import app.bot.templates as templates
from app.bot.mvc import RequestContainer
from app.bot.reqhandler import RequestHandlerState, StateChanger
from app.bot.states import GameChosenState
from app.core import GamesRegistry
from app.dao import Database
from app.dao.solutions_dao import SolutionsDao

re_info_cmd = re.compile("^/i_(.+)$")


class DefaultRequestHandlerState(RequestHandlerState):
    def __init__(self, games_registry: GamesRegistry = None, database: Database = None,
                 solutions_dao: SolutionsDao = None):
        self.games_registry = games_registry
        self.database = database
        self.solutions_dao = solutions_dao

    def handle(self, state_changer: StateChanger, request_container: RequestContainer):
        req = request_container.request

        if req.is_command('start') or req.has_text(buttons.button_back):
            request_container.add_template_reply(templates.start_message)
        elif req.has_text(buttons.button_about):
            request_container.add_template_reply(templates.about_bot)
        elif req.has_text(buttons.button_solutions_list):
            games = self.games_registry.get_games_list()
            solutions = self.solutions_dao.find_solutions_by_creator(req.effective_user_id)

            request_container.add_template_reply(templates.solutions_list, {
                'solutions': solutions,
                'games': games
            })
        else:
            match_info_cmd = req.match_text(re_info_cmd)

            if match_info_cmd:
                game_name = match_info_cmd.group(1)
                game = self.games_registry.get_by_name(game_name)
                solution = self.solutions_dao.find_solution(req.effective_user_id, game_name)

                request_container.add_template_reply(templates.solution_info, {
                    'solution': solution,
                    'game': game
                })
                state_changer.change(GameChosenState(game, self.database, self.solutions_dao))
