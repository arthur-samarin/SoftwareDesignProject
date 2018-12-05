from typing import List, Optional

import app.bot.buttons as buttons
from app.bot.mvc import Template, MessageContent
from app.core import Game
from app.model import Solution
from app.util import group_by_k

err_no_such_game = Template.constant_html('Такая игра не существует')
err_no_solution = Template.from_string_format('У тебя нет решения для игры 🕹{name}!')

start_message = Template.constant(MessageContent('''
Добро пожаловать, разработчик!

Здесь ты можешь показать всем свои навыки в разработке ИИ для пошаговых игр.
''', buttons.default_set))

main_message = Template.constant(MessageContent('''
Что ты хочешь узнать?
''', buttons.default_set))

about_bot = Template.constant(MessageContent('''
<b>❓ О боте</b>

Этот бот сделан в качесте проекта по курсу проектирования ПО.
''', buttons.default_set))

upload_solution = Template.constant(MessageContent('Отправь мне файл с кодом твоего решения', buttons.cancel_button_set))
upload_solution_too_big = Template.constant(MessageContent('Размер решения не должен превышать 1Мб', buttons.cancel_button_set))
upload_solution_ok = Template.constant(MessageContent('Решение обновлено'))
rename_solution = Template.constant(MessageContent('Введи новое название своего решения.\n'
                                                   '3-20 символов. Русские и латинские буквы, цифры, пробелы и _.', buttons.cancel_button_set))
rename_solution_ok = Template.constant(MessageContent('Имя решения обновлено.'))
challenge_link = Template.from_string_format('Кинь эту команду тому, с кем ты хочешь сразиться:\n\n{link}')


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
                text += solution.name_as_html
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
            text += solution.name_as_html + '\n'
            text += 'Язык: ' + solution.language_name + '\n'
            text += '\n'
        else:
            text += '<i>Решения нет</i>\n'

        return MessageContent(text, buttons.solution_actions_set if solution else buttons.no_solution_actions_set)


solution_info = _SolutionInfo()


class _ChooseLanguage(Template):
    def create_message(self, args: dict) -> MessageContent:
        button_rows = group_by_k(3, list(map(lambda l: l.display_name, args['list'])))
        return MessageContent('Выбери язык твоего решения.', button_rows)


choose_language = _ChooseLanguage()
