from abc import ABC, abstractmethod
from enum import Enum

from app.core import GameOutcome, Game
from app.model import SourceCode

import random


class GameOutcomeReason(Enum):
    OK = 1
    INVALID_MOVE = 2
    TIMEOUT = 3
    CRASH = 4


class GameVerdict:
    def __init__(self, outcome: GameOutcome, reason: GameOutcomeReason):
        self.outcome = outcome
        self.reason = reason


class CheckingSystem(ABC):
    @abstractmethod
    def evaluate(self, game: Game, id1: str, source1: SourceCode, id2: str, source2: SourceCode) -> GameVerdict:
        raise NotImplementedError()


class RandomCheckingSystem(CheckingSystem):
    def evaluate(self, game: Game, id1: str, source1: SourceCode, id2: str, source2: SourceCode) -> GameVerdict:
        c1 = random.randint(0, len(source1.code))
        c2 = random.randint(0, len(source2.code))
        if c1 > c2:
            outcome = GameOutcome.FIRST_WIN
        elif c1 == c2:
            outcome = GameOutcome.TIE
        else:
            outcome = GameOutcome.SECOND_WIN

        return GameVerdict(outcome, GameOutcomeReason.OK)
