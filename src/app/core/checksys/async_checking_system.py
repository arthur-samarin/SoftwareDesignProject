from concurrent.futures import Future, Executor

from app.core.checksys import CheckingSystem, GameVerdict
from app.model import SourceCode


class AsyncCheckingSystem:
    def __init__(self, wrapped: CheckingSystem, executor: Executor):
        self.wrapped = wrapped
        self.executor = executor

    def async_evaluate(self, id1: str, source1: SourceCode, id2: str, source2: SourceCode) -> Future:
        def run() -> GameVerdict:
            return self.wrapped.evaluate(id1, source1, id2, source2)

        return self.executor.submit(run)
