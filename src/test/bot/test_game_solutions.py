from app.bot import templates, buttons
from app.bot.mvc.file_handle import MemoryFileHandle
from app.core import Game, Language
from app.model import SourceCode, Solution
from test.bot import AppTestCase


class TestGameSolutions(AppTestCase):
    def setUp(self) -> None:
        self.g1 = Game('g1', 'Game 1')
        self.g2 = Game('g2', 'Game 2')
        self.l1 = Language('l1', 'Lang 1')
        self.l2 = Language('l2', 'Lang 2')
        self.set_up_app(games=[self.g1, self.g2], languages=[self.l1, self.l2])

    def tearDown(self) -> None:
        self.tear_down_app()

    def test_no_solutions(self) -> None:
        # 'Games' button -> list of games, no solutions
        args = self.assert_has_answer(buttons.button_games, templates.solutions_list)
        self.assertEquals([], args['solutions'])

    def test_solution_is_shown(self) -> None:
        # Solution exists
        self.components.solutions_dao.create_solution(42, self.g1.name, SourceCode('a.py', b'print()', self.l1.name))
        # 'Games' button -> list of games, contains solution
        args = self.assert_has_answer(buttons.button_games, templates.solutions_list)
        self.assertEquals(1, len(args['solutions']))
        sol1: Solution = args['solutions'][0]
        self.assertIsNone(sol1.name)
        self.assertEquals(sol1.game_name, self.g1.name)
        self.assertEquals(sol1.language_name, self.l1.name)
        self.assertEquals(sol1.filename, 'a.py')
        self.assertEquals(sol1.code, b'print()')
        # /i_<game> - shows solution info
        args = self.assert_has_answer('/i_' + self.g1.name, templates.solution_info)
        game1: Game = args['game']
        self.assertEquals(game1, self.g1)
        sol1: Solution = args['solution']
        self.assertIsNone(sol1.name)
        self.assertEquals(sol1.game_name, self.g1.name)
        self.assertEquals(sol1.language_name, self.l1.name)
        self.assertEquals(sol1.filename, 'a.py')
        self.assertEquals(sol1.code, b'print()')

    def test_solution_upload(self) -> None:
        # /i_<game>
        self.assert_has_answer('/i_' + self.g2.name, templates.solution_info)
        # 'Upload solution'
        # First: language selection
        self.assert_has_answer(buttons.button_upload, templates.choose_language)
        self.assert_has_answer(self.l2.display_name, templates.upload_solution)
        # Second: solution upload
        self.assert_has_answers(
            MemoryFileHandle('c.py', b'print()'),
            templates.upload_solution_ok, templates.solution_info
        )
        # Check that solution exists
        sol = self.components.solutions_dao.find_solution(42, self.g2.name)
        self.assertIsNone(sol.name)
        self.assertEqual(sol.filename, 'c.py')
        self.assertEqual(sol.code, b'print()')
        self.assertEqual(sol.language_name, self.l2.name)
        self.assertEqual(sol.game_name, self.g2.name)

    def test_solution_rename(self) -> None:
        # Create solution in database
        self.components.solutions_dao.create_solution(42, self.g2.name, SourceCode('ddd.py', b'print()', self.l1.name))
        # /i_<game> -> rename
        self.assert_has_answer('/i_' + self.g2.name, templates.solution_info)
        self.assert_has_answer(buttons.button_rename, templates.rename_solution)
        self.assert_has_answers('THE BEST SOLUTION', templates.rename_solution_ok, templates.solution_info)
        # Check solution in database
        sol = self.components.solutions_dao.find_solution(42, self.g2.name)
        self.assertEqual(sol.name, 'THE BEST SOLUTION')
        self.assertEqual(sol.language_name, self.l1.name)
        self.assertEqual(sol.filename, 'ddd.py')
        self.assertEqual(sol.code, b'print()')
