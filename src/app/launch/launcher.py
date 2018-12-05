import logging
from telegram import Bot
from telegram.utils.request import Request

from app.bot import Components
from app.bot import AppRequestHandler
from app.bot.mvc import MvcBotRunner
from app.core import GamesRegistry, Game, LanguageRegistry, Language
from app.dao import Database
from app.dao.solutions_dao import SolutionsDao
from .config import Config


class Launcher:
    @staticmethod
    def start(config: Config):
        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                            level=logging.INFO)

        database = Database('sqlite:///main.db')
        database.setup()

        games_registry = GamesRegistry()
        games_registry.register(Game('xo3', 'Крестики-нолики 3x3'))
        games_registry.register(Game('xo10', 'Крестики-нолики 10x10'))

        languages_registry = LanguageRegistry()
        languages_registry.register(Language('python3', 'Python 3'))
        languages_registry.register(Language('g++', 'g++ (C++17)'))

        solutions_dao = SolutionsDao(database)

        components = Components(
            database = database,
            solutions_dao = solutions_dao,
            games_registry = games_registry,
            languages_registry = languages_registry
        )

        request_handler = AppRequestHandler(components)
        bot = Bot(config.bot_token, request=Request(con_pool_size=8, proxy_url=config.proxy_url))
        bot_runner = MvcBotRunner(bot, request_handler)
        bot_runner.run()
