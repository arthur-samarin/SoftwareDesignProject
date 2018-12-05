from abc import ABC, abstractmethod
from typing import Optional

from app.core import GameOutcome


class RatingSystem(ABC):
    @abstractmethod
    def update_rating(self, rating_1: Optional[int], rating_2: Optional[int], outcome: GameOutcome) -> (int, int):
        raise NotImplementedError()


class EloRatingSystem(RatingSystem):
    def __init__(self, default_rating: int = 1000, k: int = 40):
        self.default_rating = default_rating
        self.k = k

    def update_rating(self, rating_1: Optional[int], rating_2: Optional[int], outcome: GameOutcome) -> (int, int):
        rating_1 = rating_1 if rating_1 is not None else self.default_rating
        rating_2 = rating_2 if rating_2 is not None else self.default_rating

        # Expected scores for players 1, 2
        e1 = 1/(1 + 10**((rating_2 - rating_1)/400))
        e2 = 1/(1 + 10**((rating_1 - rating_2)/400))

        # Actual scores for players 1, 2
        s1 = 1 if outcome == GameOutcome.FIRST_WIN else (0 if outcome == GameOutcome.SECOND_WIN else 0.5)
        s2 = 1 - s1

        return round(rating_1 + self.k * (s1 - e1)), round(rating_2 + self.k * (s2 - e2))
