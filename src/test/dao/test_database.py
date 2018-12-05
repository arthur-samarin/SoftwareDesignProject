from app.model import Solution
from test.dao import DatabaseTestCase


class CrashException(Exception):
    pass


class TestDatabase(DatabaseTestCase):
    def test_setup_does_not_fail_on_existing_database(self):
        # Database is already set up in DatabaseTestCase.setUp
        self.db.setup()

    def test_transaction_rollback(self):
        exception_thrown = False
        try:
            with self.db.tx() as s:
                sol = Solution(id = 1, creator_id=1, filename='a.py', code=b'X', language_name='python3', game_name='g1', version=1)
                s.add(sol)
                sol = s.query(Solution).filter(Solution.id == 1).one_or_none()
                self.assertIsNotNone(sol)
                raise CrashException('Test error')
        except CrashException:
            exception_thrown = True

        self.assertTrue(exception_thrown)
        with self.db.tx() as s:
            sol = s.query(Solution).filter(Solution.id == 1).one_or_none()
            self.assertIsNone(sol)
