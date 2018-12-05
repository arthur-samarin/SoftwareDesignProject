import logging
from concurrent.futures.thread import ThreadPoolExecutor
from telegram import Bot
from telegram.utils.request import Request

from app.bot import Components
from app.bot import AppRequestHandler
from app.bot.mvc import MvcBotRunner
from app.bot.notification_service import BotNotificationService
from app.core import GamesRegistry, Game, LanguageRegistry, Language, EloRatingSystem
from app.core.checksys import RandomCheckingSystem
from app.core.checksys.async_checking_system import ThreadPoolCheckingSystem
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

        checking_system = ThreadPoolCheckingSystem(
            RandomCheckingSystem(),
            ThreadPoolExecutor(8)
        )

        solutions_dao = SolutionsDao(database)

        bot = Bot(config.bot_token, request=Request(con_pool_size=8, proxy_url=config.proxy_url))
        components = Components(
            database = database,
            solutions_dao = solutions_dao,
            games_registry = games_registry,
            languages_registry = languages_registry,
            checking_system = checking_system,
            rating_system = EloRatingSystem(1000, 40),
            notification_service = BotNotificationService(bot)
        )

        request_handler = AppRequestHandler(components)
        bot_runner = MvcBotRunner(bot, request_handler)
        bot_runner.run()
