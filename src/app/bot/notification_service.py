import logging
from abc import ABC, abstractmethod
from telegram import Bot, ReplyKeyboardMarkup

from app.bot.mvc import Template


logger = logging.getLogger(__name__)


class NotificationService(ABC):
    @abstractmethod
    def notify_user(self, user_id: int, template: Template, args: dict):
        raise NotImplementedError()


class BotNotificationService(NotificationService):
    def __init__(self, bot: Bot):
        self.bot = bot

    def notify_user(self, user_id: int, template: Template, args: dict):
        try:
            content = template.create_message(args)
            reply_markup = ReplyKeyboardMarkup(content.buttons, resize_keyboard=True) if content.buttons else None
            self.bot.send_message(user_id, content.text, parse_mode='html', reply_markup=reply_markup)
        except:
            logger.exception('Error sending notification to user')

