import logging
import re
from concurrent.futures import Future

from app.bot import buttons, templates
from app.bot import Components
from app.bot.exceptions import NoSolutionException
from app.bot.mvc import RequestContainer, RequestHandler
from app.bot.reqhandler import BotException, StateBasedRequestHandler
from app.bot.states import GameChosenState
from app.core.checksys import GameVerdict
from app.model import SolutionLink

re_info_cmd = re.compile("^/i_(.+)$")
logger = logging.getLogger(__name__)


class AnyStateRequestHandler(RequestHandler):
    def __init__(self, components: Components, state_based_handler: StateBasedRequestHandler):
        self.components = components
        self.games_registry = components.games_registry
        self.database = components.database
        self.solutions_dao = components.solutions_dao
        self.state_based_handler = state_based_handler

    def handle(self, request_container: RequestContainer):
        req = request_container.request
        match_info_cmd = req.match_text(re_info_cmd)
        solution_link = SolutionLink.from_command(req.text) if req.text else None

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
        elif match_info_cmd:
            game_name = match_info_cmd.group(1)
            game = self.games_registry.get_by_name(game_name)
            self.state_based_handler.change_state(GameChosenState(game, self.components), request_container)
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
                    old_rating = (solution_1.rating, solution_2.rating)
                    new_rating = old_rating

                    if solution_1.creator_id != solution_2.creator_id:
                        # Update rating
                        with self.components.database.tx():
                            s1 = self.components.solutions_dao.find_by_id(solution_1.id)
                            s2 = self.components.solutions_dao.find_by_id(solution_2.id)
                            old_rating = (s1.rating, s2.rating)
                            new_rating1, new_rating2 = self.components.rating_system.update_rating(s1.rating,
                                                                                                   s2.rating,
                                                                                                   v.outcome)
                            s1.rating = new_rating1
                            s2.rating = new_rating2
                            new_rating = (new_rating1, new_rating2)

                    args = {
                        'verdict': v,
                        'sol1': solution_1,
                        'sol2': solution_2,
                        'old_rating': old_rating,
                        'new_rating': new_rating
                    }

                    self.components.notification_service.notify_user(solution_1.creator_id,
                                                                     templates.duel_result_notification,
                                                                     {**args, 'user_id': solution_1.creator_id})

                    if solution_1.creator_id != solution_2.creator_id:
                        self.components.notification_service.notify_user(solution_2.creator_id,
                                                                         templates.duel_result_notification,
                                                                         {**args, 'user_id': solution_2.creator_id})
                except:
                    logger.exception('Error handling finished duel')

            verdict_future.add_done_callback(on_duel_finished)
        else:
            # If still is not handled...
            request_container.add_template_reply(templates.main_message, {})

        request_container.stop_handling()
