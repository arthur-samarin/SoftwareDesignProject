import logging
import re
from concurrent.futures import Future

import app.bot.buttons as buttons
import app.bot.templates as templates
from app.bot import Components
from app.bot.exceptions import NoSolutionException
from app.bot.mvc import RequestContainer
from app.bot.reqhandler import RequestHandlerState, StateChanger, BotException
from app.bot.states import GameChosenState
from app.core.checksys import GameVerdict
from app.model import SolutionLink

re_info_cmd = re.compile("^/i_(.+)$")
logger = logging.getLogger(__name__)

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
        elif req.has_text(buttons.button_games):
            games = self.games_registry.get_games_list()
            solutions = self.solutions_dao.find_solutions_by_creator(req.effective_user_id)

            request_container.add_template_reply(templates.solutions_list, {
                'solutions': solutions,
                'games': games
            })
        else:
            match_info_cmd = req.match_text(re_info_cmd)
            solution_link = SolutionLink.from_command(req.text) if req.text else None

            if match_info_cmd:
                game_name = match_info_cmd.group(1)
                game = self.games_registry.get_by_name(game_name)

                state_changer.change(GameChosenState(game, self.components), request_container)
            elif solution_link:
                solution_2 = self.solutions_dao.find_solution(solution_link.creator_id, solution_link.game_name)
                if solution_2 is None:
                    raise BotException(templates.duel_failed_bad_link, {})
                game = self.components.games_registry.get_by_name(solution_link.game_name)
                solution_1 = self.solutions_dao.find_solution(req.effective_user_id, solution_link.game_name)
                if solution_1 is None:
                    raise NoSolutionException(game)

                request_container.add_template_reply(templates.duel_started, {})
                verdict_future: Future = self.components.checking_system.async_evaluate(
                    game, solution_1.id_with_version, solution_1.source_code,
                    solution_2.id_with_version, solution_2.source_code
                )

                def on_duel_finished(_):
                    try:
                        v: GameVerdict = verdict_future.result()

                        if solution_1.creator_id != solution_2.creator_id:
                            # Update rating
                            with self.components.database.tx():
                                s1 = self.components.solutions_dao.find_by_id(solution_1.id)
                                s2 = self.components.solutions_dao.find_by_id(solution_2.id)
                                new_rating1, new_rating2 = self.components.rating_system.update_rating(s1.rating, s2.rating, v.outcome)
                                s1.rating = new_rating1
                                s2.rating = new_rating2
                    except:
                        logger.exception('Error handling finished duel')

                    self.components.notification_service.notify_user(solution_1.creator_id, templates.duel_result_notification, {})
                    self.components.notification_service.notify_user(solution_2.creator_id, templates.duel_result_notification, {})

                verdict_future.add_done_callback(on_duel_finished)
            else:
                request_container.add_template_reply(templates.main_message, {})

