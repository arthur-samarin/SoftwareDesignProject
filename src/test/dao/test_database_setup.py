from test.dao import DatabaseTestCase


class TestDatabaseSetup(DatabaseTestCase):
    def test_setup_does_not_fail_on_existing_database(self):
        # Database is already set up in DatabaseTestCase.setUp
        self.db.setup()
