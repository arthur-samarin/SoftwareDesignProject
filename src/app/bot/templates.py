import html
from typing import List, Optional

import app.bot.buttons as buttons
from app.bot.mvc import Template, MessageContent
from app.core import Game
from app.model import Solution
from app.util import group_by_k

err_no_such_game = Template.constant_html('Такая игра не существует')

start_message = Template.constant(MessageContent('''
Добро пожаловать, разработчик!

Здесь ты можешь показать всем свои навыки в разработке ИИ для пошаговых игр.
''', buttons.default_set))

about_bot = Template.constant(MessageContent('''
<b>❓ О боте</b>

Этот бот сделан в качесте проекта по курсу проектирования ПО.
''', buttons.default_set))

upload_solution = Template.constant_html('Отправь мне файл с кодом твоего решения')
rename_solution = Template.constant_html('Введи новое название своего решения.\nОтменить: /cancel')


class _SolutionsList(Template):
    def create_message(self, args: dict) -> MessageContent:
        text = '<b>Игры:</b>\n\n'
        games: List[Game] = args['games']
        solutions: List[Solution] = args['solutions']
        game_name_to_solution = dict(map(lambda sol: (sol.game_name, sol), solutions))

        for game in games:
            text += game.display_name + ": "

            solution: Solution = game_name_to_solution.get(game.name)
            if solution is not None:
                text += html.escape(solution.name)
            else:
                text += '<i>[нет решения]</i>'

            text += ', /i_' + game.name
            text += '\n'

        return MessageContent(text, buttons.default_set)


solutions_list = _SolutionsList()


class _SolutionInfo(Template):
    def create_message(self, args: dict) -> MessageContent:
        game: Game = args['game']
        solution: Optional[Solution] = args['solution']

        text = f'<b>🕹 {game.display_name}</b>\n\n'
        if solution:
            text += html.escape(game.name if game.name else '[без имени]') + '\n'
            text += 'Язык: ' + solution.language_name + '\n'
            text += '\n'
        else:
            text += '<i>Решения нет</i>\n'

        return MessageContent(text, buttons.solution_actions_set if solution else buttons.no_solution_actions_set)


solution_info = _SolutionInfo()


class _ChooseLanguage(Template):
    def create_message(self, args: dict) -> MessageContent:
        button_rows = group_by_k(3, args['list'])
        return MessageContent('Выбери язык твоего решения.', group_by_k(3, button_rows))


choose_language = _ChooseLanguage()
