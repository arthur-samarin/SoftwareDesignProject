from typing import List

from app.core import Game


class GamesRegistry:
    def __init__(self):
        self.games_dict = {}

    def register(self, game: Game):
        name = game.name
        if name in self.games_dict:
            raise RuntimeError('Game "{}" is already registered'.format(name))
        self.games_dict[name] = game

    def get_by_name(self, name: str):
        return self.games_dict[name]

    def get_games_list(self):
        l = list(self.games_dict.values())
        l.sort(key=lambda game: game.name)
        return l

    @staticmethod
    def from_games(games: List[Game]) -> 'GamesRegistry':
        r = GamesRegistry()
        for g in games:
            r.register(g)
        return r
