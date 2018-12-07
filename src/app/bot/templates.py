from typing import List, Optional

from app.bot import buttons
from app.bot.mvc import Template, MessageContent
from app.core import Game, GameOutcome
from app.core.checksys import GameVerdict
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

duel_started = Template.constant_html('Ты бросил вызов! Жди результата.')
duel_failed_bad_link = Template.constant_html('Что-то странное. Не могу найти решение по ссылке.')
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
                text += solution.name_rating_as_html
            else:
                text += '<i>[нет решения]</i>'

            text += ', /i_' + game.name
            text += '\n'

        return MessageContent(text, buttons.default_set)


solutions_list = _SolutionsList()


class _SolutionInfo(Template):
    def create_message(self, args: dict) -> MessageContent:
        game: Game = args['game']
        top_solutions: List[Solution] = args['top']
        solution: Optional[Solution] = args['solution']

        text = f'<b>🕹 {game.display_name}</b>\n\n'
        if solution:
            text += solution.name_rating_as_html + '\n'
            text += 'Язык: ' + solution.language_name + '\n'
        else:
            text += '<i>Решения нет</i>\n'

        text += '\n'
        for i, s in enumerate(top_solutions):
            index = i + 1
            text += '<b>#{}</b> {}\n{}\n'.format(index, s.name_rating_as_html, s.create_link().to_command())

        return MessageContent(text, buttons.solution_actions_set if solution else buttons.no_solution_actions_set)


solution_info = _SolutionInfo()


class _ChooseLanguage(Template):
    def create_message(self, args: dict) -> MessageContent:
        button_rows = group_by_k(3, list(map(lambda l: l.display_name, args['list'])))
        return MessageContent('Выбери язык твоего решения.', button_rows)


choose_language = _ChooseLanguage()


class _DuelResultNotification(Template):
    def create_message(self, args: dict) -> MessageContent:
        user_id = args['user_id']
        sol1: Solution = args['sol1']
        sol2: Solution = args['sol2']
        or1, or2 = args['old_rating']
        nr1, nr2 = args['new_rating']
        verdict: GameVerdict = args['verdict']
        outcome = verdict.outcome

        def format_solution(s: Solution):
            return '👤{}'.format(s.name_as_html) if s.creator_id == user_id else s.name_as_html

        # Кто с кем (своё жирное)
        text = '<b>⚔️ Состоялась дуэль! ⚔️</b>\n'
        text += format_solution(sol1) + ' <i>VS</i> ' + format_solution(sol2) + '\n\n'

        # Кто победил
        if verdict.outcome == GameOutcome.FIRST_WIN:
            text += '<b>Победитель: </b> игрок 1, ' + format_solution(sol1)
        elif verdict.outcome == GameOutcome.TIE:
            text += '<b>Ничья</b>'
        else:
            text += '<b>Победитель: </b> игрок 2, ' + format_solution(sol2)
        text += '\n\n'

        # Изменение рейтинга
        text += '<b>Рейтинг</b>: '
        if or1 == nr1 and or2 == nr2:
            text += 'без изменений'
        else:
            def format_rating_change(old_r, new_r):
                if old_r is not None and new_r is not None:
                    delta = new_r - old_r
                    delta_str = ('+' + str(delta)) if delta > 0 else str(delta)
                    return f'{old_r} ➡️ {new_r} ({delta_str})'
                else:
                    return str(new_r)

            text += '\n'
            text += '<b>Игрок 1: </b>' + format_rating_change(or1, nr1) + '\n'
            text += '<b>Игрок 2: </b>' + format_rating_change(or2, nr2) + '\n'

        return MessageContent(text)


duel_result_notification = _DuelResultNotification()
