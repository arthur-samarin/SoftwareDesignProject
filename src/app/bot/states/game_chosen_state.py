import app.bot.buttons as buttons
import app.bot.templates as templates
from app.bot import Components
from app.bot.exceptions import NoSolutionException
from app.bot.mvc import RequestContainer
from app.bot.reqhandler import RequestHandlerState, StateChanger
from app.core import Game, LanguageRegistry
from app.dao import Database
from app.dao.solutions_dao import SolutionsDao
from app.model import SourceCode

import re


class GameSolutionChangeNameState(RequestHandlerState):
    solution_name_regex = re.compile('^[a-zA-Z0-9А-Яа-яёЁ _]{3,20}$')

    def __init__(self, game: Game, components: Components):
        self.game = game

        self.components = components
        self.database: Database = components.database
        self.solutions_dao: SolutionsDao = components.solutions_dao

    def on_enter(self, request_container: RequestContainer) -> None:
        request_container.add_template_reply(templates.rename_solution, {})

    def handle(self, state_changer: StateChanger, request_container: RequestContainer) -> None:
        req = request_container.request

        if req.has_text(buttons.button_cancel):
            # Cancel: move back
            state_changer.change(GameChosenState(self.game, self.components), request_container)
        elif req.match_text(self.solution_name_regex):
            # New name -> rename
            with self.database.tx():
                solution = self.solutions_dao.find_solution(req.effective_user_id, self.game.name)
                if solution is None:
                    raise NoSolutionException(self.game)
                solution.name = req.text

            request_container.add_template_reply(templates.rename_solution_ok, {})
            state_changer.change(GameChosenState(self.game, self.components), request_container)
            return
        else:
            # Anything else -> show message
            self.on_enter(request_container)


class GameSolutionUploadState(RequestHandlerState):
    def __init__(self, game: Game, components: Components):
        self.game = game

        self.components = components
        self.database: Database = components.database
        self.solutions_dao: SolutionsDao = components.solutions_dao
        self.languages_registry: LanguageRegistry = components.languages_registry

        self.chosen_language = None

    def on_enter(self, request_container: RequestContainer) -> None:
        if self.chosen_language is None:
            request_container.add_template_reply(templates.choose_language,
                                                 {'list': self.languages_registry.get_languages_list()})
        else:
            request_container.add_template_reply(templates.upload_solution, {})

    def handle(self, state_changer: StateChanger, request_container: RequestContainer) -> None:
        req = request_container.request

        if req.has_text(buttons.button_cancel):
            # Cancel -> jump to GameChosenState
            state_changer.change(GameChosenState(self.game, self.components), request_container)
            return

        if self.chosen_language and req.get_file_handle():
            # File -> upload file
            max_file_size = 2 ** 20  # 1 MiB
            file_handle = req.get_file_handle()

            if file_handle.size() > max_file_size:
                request_container.add_template_reply(templates.upload_solution_too_big, {})
                return

            name = file_handle.name()
            content = file_handle.content()

            self.solutions_dao.create_solution(req.effective_user_id, self.game.name,
                                               SourceCode(name, content, self.chosen_language.name))
            request_container.add_template_reply(templates.upload_solution_ok)
            state_changer.change(GameChosenState(self.game, self.components), request_container)
        elif not self.chosen_language and req.text and self.languages_registry.get_by_display_name(req.text):
            language = self.languages_registry.get_by_display_name(req.text)
            self.chosen_language = language
            self.on_enter(request_container)
        else:
            # Anything else -> show message
            self.on_enter(request_container)


class GameChosenState(RequestHandlerState):
    def __init__(self, game: Game, components: Components):
        self.game = game

        self.components = components
        self.database: Database = components.database
        self.solutions_dao: SolutionsDao = components.solutions_dao

    def on_enter(self, request_container: RequestContainer) -> None:
        req = request_container.request
        solution = self.solutions_dao.find_solution(req.effective_user_id, self.game.name)
        request_container.add_template_reply(templates.solution_info, {
            'solution': solution,
            'game': self.game
        })

    def handle(self, state_changer: StateChanger, request_container: RequestContainer) -> None:
        req = request_container.request

        if req.has_text(buttons.button_upload):
            # 'Upload Solution' -> change to upload state
            state_changer.change(GameSolutionUploadState(self.game, self.components), request_container)
        elif req.has_text(buttons.button_rename):
            # 'Rename Solution' -> change to rename state
            state_changer.change(GameSolutionChangeNameState(self.game, self.components), request_container)
        elif req.has_text(buttons.button_challenge):
            # 'Challenge' -> show challenge link
            solution = self.solutions_dao.find_solution(req.effective_user_id, self.game.name)
            if solution is None:
                raise NoSolutionException(self.game)
            request_container.add_template_reply(templates.challenge_link, {
                'link': solution.create_link().to_command()
            })
        else:
            # Unknown command: switch to default state
            state_changer.change_and_handle(None, request_container)
