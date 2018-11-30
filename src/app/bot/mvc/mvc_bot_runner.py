import logging

from telegram import Bot, Update
from telegram.ext import Updater, Handler, Dispatcher

from app.bot.mvc import RequestHandler, RequestContainer, Request

logger = logging.getLogger(__name__)


class MvcBotRunner:
    def __init__(self, bot: Bot, request_handler: RequestHandler):
        self.bot = bot
        self.request_handler = request_handler
        self.updater = Updater(bot=self.bot)
        self.updater.dispatcher.add_handler(MvcHandler(self.bot, self.request_handler))

    def run(self):
        self.updater.start_polling()

    def stop(self):
        self.updater.stop()


class MvcHandler(Handler):
    def __init__(self, bot: Bot, request_handler: RequestHandler):
        super().__init__(None)
        self.bot = bot
        self.request_handler = request_handler

    def check_update(self, update) -> bool:
        return True

    def handle_update(self, update: Update, dispatcher: Dispatcher) -> None:
        request_container = RequestContainer(Request(update))
        try:
            self.request_handler.handle(request_container)
        except Exception:
            logger.exception('Exception while handling request with RequestHandler')

        for response in request_container.responses:
            try:
                response.send(self.bot, request_container.request)
            except Exception:
                logger.exception('Exception while sending response')
