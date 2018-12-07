from typing import List

from app.bot.mvc import RequestContainer


class RequestHandler:
    def handle(self, container: RequestContainer) -> None:
        raise NotImplementedError()


class SequentialRequestHandler(RequestHandler):
    def __init__(self, subhandlers: List[RequestHandler]):
        self.subhandlers = subhandlers

    def handle(self, container: RequestContainer) -> None:
        for subhandler in self.subhandlers:
            if not container.handling_completed:
                subhandler.handle(container)
            else:
                break
