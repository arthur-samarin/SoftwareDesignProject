from typing import Optional

from app.bot.mvc import Template, Response, ResponseReplyTemplate


class BotException(Exception):
    def __init__(self, template: Template, args: dict):
        message_content = template.create_message(args)
        super().__init__(message_content.text)

        self.template = template
        self.template_args = args

    def to_response(self) -> Optional[Response]:
        return ResponseReplyTemplate(self.template, self.template_args)
