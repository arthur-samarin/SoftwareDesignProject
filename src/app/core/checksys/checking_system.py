from abc import ABC, abstractmethod
from enum import Enum

from app.core import GameOutcome
from app.model import SourceCode


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
    def evaluate(self, id1: str, source1: SourceCode, id2: str, source2: SourceCode) -> GameVerdict:
        raise NotImplementedError()
