from app.bot.mvc import RequestContainer


class RequestHandler:
    def handle(self, container: RequestContainer) -> None:
        raise NotImplementedError()
