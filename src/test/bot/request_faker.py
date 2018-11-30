from datetime import datetime

from telegram import Update, User, Message, Chat

from app.bot.mvc import Request


class RequestFaker:
    @staticmethod
    def text_message(text='Test', user_id: int = 42):
        update = Update(1, message=Message(1, chat=Chat(user_id, Chat.PRIVATE),
                                           text=text,
                                           from_user=User(user_id, first_name="Test", last_name="Test", is_bot=False),
                                           date=datetime(2018, 10, 10, 1, 2, 3)))
        return Request(update)
