from typing import Optional, List

from app.dao import Database
from app.model import SourceCode, Solution


class SolutionsDao:
    def __init__(self, db: Database):
        self.db = db

    def create_solution(self, creator_id: int, game_name: str, source_code: SourceCode) -> Solution:
        with self.db.tx() as s:
            solution = self.find_solution(creator_id, game_name)
            if solution is None:
                solution = Solution(creator_id=creator_id, game_name=game_name)
                solution.version = 1
            else:
                solution.version += 1

            solution.source_code = source_code
            s.add(solution)

            return solution

    def find_by_id(self, id: int) -> Solution:
        with self.db.tx() as s:
            return s.query(Solution).filter(Solution.id == id).one()

    def find_solution(self, creator_id: int, game_name: str) -> Optional[Solution]:
        with self.db.tx() as s:
            solution = s.query(Solution).filter(Solution.creator_id == creator_id,
                                                Solution.game_name == game_name).one_or_none()
            return solution

    def find_solutions_by_creator(self, creator_id: int) -> List[Solution]:
        with self.db.tx() as s:
            return s.query(Solution).filter(Solution.creator_id == creator_id).all()

    def solutions_top(self, game_name: str, limit: int):
        with self.db.tx() as s:
            return list(s.query(Solution).filter(Solution.game_name == game_name, Solution.rating != None)\
                    .order_by(Solution.rating.desc()).limit(limit).all())

