from app.bot.mvc import Request, Response, ResponseReplyTemplate, Template


class RequestContainer:
    def __init__(self, request: Request):
        self.request = request
        self.responses = []

    def add_response(self, response: Response):
        self.responses.append(response)

    def add_template_reply(self, template: Template, args: dict):
        self.add_response(ResponseReplyTemplate(template, args))