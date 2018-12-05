from telegram import Bot, Document


class FileHandle:
    def name(self) -> str:
        raise NotImplementedError()

    def size(self) -> int:
        raise NotImplementedError()

    def content(self) -> bytes:
        raise NotImplementedError()


class MemoryFileHandle(FileHandle):
    def __init__(self, name: str, content: bytes):
        self._name = name
        self._content = content

    def name(self) -> str:
        return self._name

    def size(self) -> int:
        return len(self._content)

    def content(self) -> bytes:
        return self._content


class RealFileHandle(FileHandle):
    def __init__(self, bot: Bot, document: Document):
        self.bot = bot
        self.document = document
        self.cached_content = None

    def name(self) -> str:
        return self.document.file_name

    def size(self) -> int:
        return self.document.file_size

    def content(self) -> bytes:
        if self.cached_content is None:
            file = self.bot.get_file(self.document.file_id)
            self.cached_content = file.download_as_bytearray()
        return self.cached_content

