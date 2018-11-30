from typing import Optional, List


class MessageContent:
    def __init__(self, text: str, buttons: Optional[List[List[str]]] = None) -> None:
        super().__init__()
        self.text = text
        self.buttons = buttons
