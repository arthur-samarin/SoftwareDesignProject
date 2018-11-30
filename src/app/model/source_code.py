class SourceCode:
    def __init__(self, filename: str, code: bytes, language_name: str):
        self.filename = filename
        self.code = code
        self.language_name = language_name
