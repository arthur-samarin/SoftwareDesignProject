import os
from typing import List, Optional

from app.core import Language


class CppLanguage(Language):
    def __init__(self):
        super().__init__('cpp17', 'C++17')

    def get_compile_command(self, file: str) -> Optional[List[str]]:
        return ['g++', '-O3', '-std=c++17', '-o', 'out', file]

    def get_run_command(self, file: str) -> List[str]:
        return [os.path.join(os.path.dirname(file), 'out')]
