import re
from typing import Optional


class SolutionLink:
    __link_regex = re.compile('^/duel_[\w_]+_\d+$')

    def __init__(self, game_name: str, creator_id: int):
        self.game_name = game_name
        self.creator_id = creator_id

    def to_command(self):
        return '/duel_{}_{}'.format(self.creator_id, self.game_name)

    @classmethod
    def from_command(cls, command) -> Optional['SolutionLink']:
        m = cls.__link_regex.match(command)
        if m:
            return SolutionLink(m.group(1), int(m.group(2)))

