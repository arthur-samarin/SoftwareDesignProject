from telegram import Bot, Message, Chat, ReplyKeyboardMarkup

from app.bot.mvc import Request, Template
from typing import Optional


class Response:
    def __init__(self):
        pass

    def send(self, bot: Bot, request: Request) -> None:
        raise NotImplementedError()


class ResponseReplyTemplate(Response):
    def __init__(self, template: Template, args: Optional[dict] = None):
        super().__init__()
        self.template = template
        self.args = args

    def send(self, bot: Bot, request: Request) -> None:
        chat: Chat = request.update.effective_chat
        message: Message = request.update.message
        request_message_id = message.message_id if message else None

        message_content = self.template.create_message(self.args)
        text = message_content.text
        reply_markup = ReplyKeyboardMarkup(keyboard=message_content.buttons) if message_content.buttons else None

        bot.send_message(chat.id, text, reply_markup=reply_markup,
                         parse_mode='html', disable_web_page_preview=True, reply_to_message_id=request_message_id)

