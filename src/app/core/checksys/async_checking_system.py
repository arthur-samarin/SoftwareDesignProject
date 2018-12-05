from abc import ABC, abstractmethod
from concurrent.futures import Future, Executor

from app.core import Game
from app.core.checksys import CheckingSystem, GameVerdict
from app.model import SourceCode


class AsyncCheckingSystem(ABC):
    @abstractmethod
    def async_evaluate(self, game: Game, id1: str, source1: SourceCode, id2: str, source2: SourceCode) -> Future:
        raise NotImplementedError()


class ThreadPoolCheckingSystem(AsyncCheckingSystem):
    def __init__(self, wrapped: CheckingSystem, executor: Executor):
        self.wrapped = wrapped
        self.executor = executor

    def async_evaluate(self, game: Game, id1: str, source1: SourceCode, id2: str, source2: SourceCode) -> Future:
        def run() -> GameVerdict:
            return self.wrapped.evaluate(game, id1, source1, id2, source2)

        return self.executor.submit(run)


class SyncCheckingSystem(AsyncCheckingSystem):
    def __init__(self, wrapped: CheckingSystem):
        self.wrapped = wrapped

    def async_evaluate(self, game: Game, id1: str, source1: SourceCode, id2: str, source2: SourceCode) -> Future:
        r = self.wrapped.evaluate(game, id1, source1, id2, source2)
        f = Future()
        f.set_result(r)
        return f

