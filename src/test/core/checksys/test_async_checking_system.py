import unittest

from concurrent.futures.thread import ThreadPoolExecutor
from typing import Callable

from app.core import GameOutcome, Game
from app.core.checksys import CheckingSystem, GameVerdict, GameOutcomeReason
from app.core.checksys.async_checking_system import ThreadPoolCheckingSystem
from app.model import SourceCode


class FakeCheckingSystem(CheckingSystem):
    def __init__(self, verdict_func: Callable[[str, str], GameVerdict]) -> None:
        super().__init__()
        self.verdict_func = verdict_func

    def evaluate(self, game: Game, id1: str, source1: SourceCode, id2: str, source2: SourceCode) -> GameVerdict:
        return self.verdict_func(id1, id2)


class TestAsyncCheckingSystem(unittest.TestCase):
    def setUp(self):
        def verdict_func(id1: str, id2: str):
            v1 = int(id1)
            v2 = int(id2)
            return GameVerdict(GameOutcome(v1), GameOutcomeReason(v2))

        self.g1 = Game('game1', 'Game 1')
        self.system = FakeCheckingSystem(verdict_func)
        self.thread_pool = ThreadPoolExecutor(4)
        self.async_system = ThreadPoolCheckingSystem(self.system, self.thread_pool)

    def tearDown(self) -> None:
        self.thread_pool.shutdown()

    def test_async_checking_system(self):
        s = SourceCode('a.py', b'print()', 'python3')
        f1 = self.async_system.async_evaluate(self.g1, str(GameOutcome.FIRST_WIN.value), s, str(GameOutcomeReason.OK.value), s)
        f2 = self.async_system.async_evaluate(self.g1, str(GameOutcome.TIE.value), s, str(GameOutcomeReason.CRASH.value), s)
        f3 = self.async_system.async_evaluate(self.g1, str(GameOutcome.SECOND_WIN.value), s, str(GameOutcomeReason.INVALID_MOVE.value), s)
        r1: GameVerdict = f1.result()
        self.assertEqual(r1.outcome, GameOutcome.FIRST_WIN)
        self.assertEqual(r1.reason, GameOutcomeReason.OK)
        r2: GameVerdict = f2.result()
        self.assertEqual(r2.outcome, GameOutcome.TIE)
        self.assertEqual(r2.reason, GameOutcomeReason.CRASH)
        r3: GameVerdict = f3.result()
        self.assertEqual(r3.outcome, GameOutcome.SECOND_WIN)
        self.assertEqual(r3.reason, GameOutcomeReason.INVALID_MOVE)
