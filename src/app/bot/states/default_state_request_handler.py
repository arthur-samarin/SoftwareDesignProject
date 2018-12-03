import re

import app.bot.buttons as buttons
import app.bot.templates as templates
from app import Components
from app.bot.mvc import RequestContainer
from app.bot.reqhandler import RequestHandlerState, StateChanger
from app.bot.states import GameChosenState

re_info_cmd = re.compile("^/i_(.+)$")


class DefaultRequestHandlerState(RequestHandlerState):
    def __init__(self, components: Components):
        self.components = components
        self.games_registry = components.games_registry
        self.database = components.database
        self.solutions_dao = components.solutions_dao

    def handle(self, state_changer: StateChanger, request_container: RequestContainer):
        req = request_container.request

        if req.is_command('start'):
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

                state_changer.change(GameChosenState(game, self.components), request_container)
            else:
                request_container.add_template_reply(templates.main_message, {})

