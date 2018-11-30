import app.bot.templates as templates
from app.bot.reqhandler import BotException


class NoSuchGameException(BotException):
    def __init__(self, game_name: str):
        super().__init__(templates.err_no_such_game, {'name': game_name})
