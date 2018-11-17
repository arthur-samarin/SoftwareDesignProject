from telegram import Update


class Request:
    def __init__(self, update: Update):
        self.update = update

    @property
    def effective_chat_id(self):
        return self.update.effective_chat.id if self.update.effective_chat else None