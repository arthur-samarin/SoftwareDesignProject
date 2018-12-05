from app.dao.solutions_dao import SolutionsDao
from app.model import SourceCode, Solution
from test.dao import DatabaseTestCase


class TestSolutionsDao(DatabaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.solutions_dao = SolutionsDao(self.db)

    def test_create_find_solution(self):
        solution = self.solutions_dao.create_solution(1, 'testgame', SourceCode('a.py', b'print("Hello")', 'python3'))

        self.assertEqual(solution.creator_id, 1)
        self.assertEqual(solution.game_name, 'testgame')
        self.assertEqual(solution.code, b'print("Hello")')
        self.assertEqual(solution.filename, 'a.py')
        self.assertEqual(solution.language_name, 'python3')

        solution = self.solutions_dao.find_solution(1, 'testgame')
        self.assertEqual(solution.creator_id, 1)
        self.assertEqual(solution.game_name, 'testgame')
        self.assertEqual(solution.code, b'print("Hello")')
        self.assertEqual(solution.filename, 'a.py')
        self.assertEqual(solution.language_name, 'python3')
        self.assertEqual(solution.version, 1)

        solution = self.solutions_dao.find_solution(1, 'testgame2')
        self.assertIsNone(solution)

        solution = self.solutions_dao.find_solution(2, 'testgame')
        self.assertIsNone(solution)

    def test_recreate_solution(self):
        self.solutions_dao.create_solution(1, 'testgame', SourceCode('a.py', b'print("Hello")', 'python3'))
        self.solutions_dao.create_solution(1, 'testgame', SourceCode('a.py', b'print("Hello, world")', 'python3'))
        solution = self.solutions_dao.find_solution(1, 'testgame')
        self.assertEqual(solution.code, b'print("Hello, world")')
        self.assertEqual(solution.version, 2)

    def test_find_solutions(self):
        self.solutions_dao.create_solution(1, 'testgame', SourceCode('a.py', b'print("Hello")', 'python3'))
        self.solutions_dao.create_solution(1, 'testgame2', SourceCode('a.py', b'print("Hello")', 'python3'))
        self.solutions_dao.create_solution(1, 'testgame', SourceCode('a.py', b'print("Hello")', 'python3'))
        self.solutions_dao.create_solution(2, 'testgame2', SourceCode('a.py', b'print("Hello")', 'python3'))

        self.assertEqual(2, len(self.solutions_dao.find_solutions_by_creator(1)))
        self.assertEqual(1, len(self.solutions_dao.find_solutions_by_creator(2)))

    def test_solutions_top(self):
        with self.db.tx() as s:
            s.add(Solution(creator_id=1, filename='a.py', code=b'', language_name='l', game_name='g1', rating=1, version=1))
            s.add(Solution(creator_id=2, filename='a.py', code=b'', language_name='l', game_name='g1', rating=5, version=1))
            s.add(Solution(creator_id=3, filename='a.py', code=b'', language_name='l', game_name='g2', rating=18, version=1))
            s.add(Solution(creator_id=4, filename='a.py', code=b'', language_name='l', game_name='g1', rating=20, version=1))
            s.add(Solution(creator_id=5, filename='a.py', code=b'', language_name='l', game_name='g1', version=1))
            s.add(Solution(creator_id=6, filename='a.py', code=b'', language_name='l', game_name='g1', rating=25, version=1))
            s.add(Solution(creator_id=7, filename='a.py', code=b'', language_name='l', game_name='g1', version=1))

        self.assertEqual([s.creator_id for s in self.solutions_dao.solutions_top('g1', 3)], [6, 4, 2])
        self.assertEqual([s.creator_id for s in self.solutions_dao.solutions_top('g2', 3)], [3])
