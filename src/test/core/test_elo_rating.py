import unittest

from app.core import GameOutcome
from app.core.rating_system import EloRatingSystem


class TestEloRating(unittest.TestCase):
    def setUp(self):
        self.rating = EloRatingSystem(1000, 40)

    def test_elo_rating_first_win(self):
        self.assertEqual(self.rating.update_rating(None, 1000, GameOutcome.FIRST_WIN), (1020, 980))
        self.assertEqual(self.rating.update_rating(1000, None, GameOutcome.FIRST_WIN), (1020, 980))
        self.assertEqual(self.rating.update_rating(None, None, GameOutcome.FIRST_WIN), (1020, 980))
        self.assertEqual(self.rating.update_rating(1000, 1000, GameOutcome.FIRST_WIN), (1020, 980))
        self.assertEqual(self.rating.update_rating(2000, 500, GameOutcome.FIRST_WIN), (2000, 500))
        self.assertEqual(self.rating.update_rating(500, 2000, GameOutcome.FIRST_WIN), (540, 1960))

    def test_elo_rating_tie(self):
        self.assertEqual(self.rating.update_rating(1000, 1000, GameOutcome.TIE), (1000, 1000))
        self.assertEqual(self.rating.update_rating(2000, 500, GameOutcome.TIE), (1980, 520))
        self.assertEqual(self.rating.update_rating(500, 2000, GameOutcome.TIE), (520, 1980))

    def test_elo_rating_second_win(self):
        self.assertEqual(self.rating.update_rating(1000, 1000, GameOutcome.SECOND_WIN), (980, 1020))
        self.assertEqual(self.rating.update_rating(2000, 500, GameOutcome.SECOND_WIN), (1960, 540))
        self.assertEqual(self.rating.update_rating(500, 2000, GameOutcome.SECOND_WIN), (500, 2000))
