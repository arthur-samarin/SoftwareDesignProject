from typing import List, Optional

from app.core import Language


class PythonLanguage(Language):
    def __init__(self):
        super().__init__('python3', 'Python 3')

    def get_compile_command(self, file: str) -> Optional[List[str]]:
        return None

    def get_run_command(self, file: str) -> List[str]:
        return ['python3', file]
