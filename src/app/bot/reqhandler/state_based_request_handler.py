from typing import Callable, Any, Optional

from app.bot.mvc import Request, RequestHandler, RequestContainer


class StateChanger:
    def change(self, new_state: Optional['RequestHandlerState']) -> None:
        raise NotImplementedError()

    def change_and_handle(self, new_state_description: Optional['RequestHandlerState'],
                          request_container: RequestContainer):
        raise NotImplementedError()


class RequestHandlerState:
    def handle(self, state_changer: StateChanger, request_container: RequestContainer):
        raise NotImplementedError()


class StateBasedRequestHandler(RequestHandler):
    chat_id_key_extractor = lambda request: request.effective_chat_id

    def __init__(self, key_extractor: Callable[[Request], Any], default_state: RequestHandlerState):
        self.key_extractor = key_extractor
        self.key_to_state = {}
        self.default_state = default_state

    def handle(self, container: RequestContainer):
        key = self.key_extractor(container.request)
        if key is not None:
            self._handle_for_key(key, container)

    def _handle_for_key(self, key: Any, request_container: RequestContainer) -> None:
        state_changer = self.__create_state_changer(key)
        state = self.key_to_state[key] if key in self.key_to_state else self.default_state
        state.handle(state_changer, request_container)

    def __create_state_changer(self, key: Any) -> StateChanger:
        return StateChangerForKey(self, key)


class StateChangerForKey(StateChanger):
    def __init__(self, request_handler: StateBasedRequestHandler, key: Any):
        self.request_handler = request_handler
        self.key = key

    def change(self, new_state_description: Optional[RequestHandlerState]) -> None:
        self.__change_state(new_state_description)

    def change_and_handle(self, new_state_description: Optional[RequestHandlerState],
                          request_container: RequestContainer) -> None:
        self.__change_state(new_state_description)
        self.request_handler._handle_for_key(self.key, request_container)

    def __change_state(self, new_state_description: Optional[RequestHandlerState]) -> None:
        if new_state_description is not None:
            self.request_handler.key_to_state[self.key] = new_state_description
        else:
            self.request_handler.key_to_state.pop(self.key)
