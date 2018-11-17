import logging

from telegram import Bot, Update
from telegram.ext import Updater, Handler

from app.bot.mvc import RequestHandler, RequestContainer, Request

logger = logging.getLogger(__name__)


class MvcBotRunner:
    def __init__(self, bot: Bot, request_handler: RequestHandler):
        self.bot = bot
        self.request_handler = request_handler
        self.updater = Updater(bot=self.bot)
        self.updater.dispatcher.add_handler(Handler(self.__handle_update))

    def run(self):
        self.updater.start_polling()

    def stop(self):
        self.updater.stop()

    def __handle_update(self, update: Update):
        request_container = RequestContainer(Request(update))
        try:
            self.request_handler.handle(request_container)
        except:
            logger.exception('Exception while handling request with RequestHandler')

        for response in request_container.responses:
            try:
                response.send(self.bot, self.request_handler)
            except:
                logger.exception('Exception while sending response')
