import logging

from telegram import Bot
from telegram.utils.request import Request

from app.bot import AppRequestHandler
from app.bot.mvc import MvcBotRunner
from .config import Config


class Launcher:
    @staticmethod
    def start(config: Config):
        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                            level=logging.INFO)

        request_handler = AppRequestHandler()
        bot = Bot(config.bot_token, request=Request(con_pool_size=8))
        bot_runner = MvcBotRunner(bot, request_handler)
        bot_runner.run()
