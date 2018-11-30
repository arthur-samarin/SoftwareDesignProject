import re

from telegram import Update


class Request:
    def __init__(self, update: Update):
        self.update = update

        self.command_name = None

        if update.message:
            text = update.message.text
            m = re.search('^/(\w+)(\s+.*)?$', text)
            if m:
                self.command_name = m.group(1)

    @property
    def effective_chat_id(self):
        return self.update.effective_chat.id if self.update.effective_chat else None

    def is_command(self, command_name):
        return self.command_name is not None and self.command_name == command_name

    def has_text(self, text):
        return self.update.message and self.update.message.text == text
