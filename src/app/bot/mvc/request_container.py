from typing import Optional

from app.bot.mvc import Request, Response, ResponseReplyTemplate, Template


class RequestContainer:
    def __init__(self, request: Request):
        self.request = request
        self.handling_completed = False
        self.responses = []

    def add_response(self, response: Response):
        self.responses.append(response)

    def add_template_reply(self, template: Template, args: Optional[dict] = None):
        self.add_response(ResponseReplyTemplate(template, args))

    def continue_handling(self):
        self.handling_completed = False

    def stop_handling(self):
        self.handling_completed = True
