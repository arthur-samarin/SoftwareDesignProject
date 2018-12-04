from datetime import datetime

from telegram import Update, User, Message, Chat
from typing import Union

from app.bot.mvc import Request, FileHandle


class RequestFaker:
    @staticmethod
    def message(content: Union[str, FileHandle] ='Test', user_id: int = 42):
        text = content if isinstance(content, str) else None
        fh = content if isinstance(content, FileHandle) else None
        update = Update(1, message=Message(1, chat=Chat(user_id, Chat.PRIVATE),
                                           text=text,
                                           from_user=User(user_id, first_name="Test", last_name="Test", is_bot=False),
                                           date=datetime(2018, 10, 10, 1, 2, 3)))
        req = Request(update, file_handle=fh)
        return req
