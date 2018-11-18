from typing import Optional, List

from app.bot.mvc import MessageContent


class Template:
    def __init__(self):
        pass

    def create_message(self, args: dict) -> MessageContent:
        raise NotImplementedError()

    @staticmethod
    def from_string_format(fmt: str, buttons: Optional[List[List]] = None):
        return StringFormatTemplate(fmt, buttons)

    @staticmethod
    def constant(content: MessageContent):
        return ConstantTemplate(content)

    @staticmethod
    def constant_html(text: str):
        return Template.constant(MessageContent(text))


class StringFormatTemplate(Template):
    def __init__(self, fmt: str, buttons: Optional[List[List]]):
        super().__init__()
        self.fmt = fmt
        self.buttons = buttons

    def create_message(self, args: dict) -> MessageContent:
        return MessageContent(self.fmt.format(**args), self.buttons)


class ConstantTemplate(Template):
    def __init__(self, content: MessageContent):
        super().__init__()
        self.content = content

    def create_message(self, args: dict) -> MessageContent:
        return self.content
