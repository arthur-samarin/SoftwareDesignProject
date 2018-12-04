import re

from telegram import Update
from typing import Pattern, Optional

from app.bot.mvc import FileHandle
from app.bot.mvc.file_handle import RealFileHandle


class Request:
    def __init__(self, update: Update, file_handle: FileHandle = None):
        self.update = update

        self.command_name = None
        self.text = None
        self.file_handle = file_handle

        if update.message:
            text = update.message.text
            self.text = text

            if text:
                m = re.search('^/(\w+)(\s+.*)?$', text)
                if m:
                    self.command_name = m.group(1)

    @property
    def effective_chat_id(self) -> Optional[int]:
        return self.update.effective_chat.id if self.update.effective_chat else None

    @property
    def effective_user_id(self) -> Optional[int]:
        return self.update.effective_user.id if self.update.effective_user else None

    def is_command(self, command_name) -> bool:
        return self.command_name is not None and self.command_name == command_name

    def has_text(self, text) -> bool:
        return self.update.message and self.update.message.text == text

    def get_file_handle(self) -> Optional[FileHandle]:
        if self.file_handle:
            return self.file_handle

        update = self.update
        if update.message and update.message.document:
            return RealFileHandle(update.message.bot, update.message.document)

    def match_text(self, regex: Pattern):
        if self.text is not None:
            return regex.match(self.text)
        else:
            return None
