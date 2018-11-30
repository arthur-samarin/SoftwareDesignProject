from unittest import TestCase

from app.dao import Database


class DatabaseTestHelper:
    def __init__(self) -> None:
        self.db = None

    def set_up(self) -> Database:
        self.db = Database('sqlite://')
        self.db.setup()
        return self.db

    def tear_down(self):
        pass


class DatabaseTestCase(TestCase):
    def setUp(self) -> None:
        self.db_helper = DatabaseTestHelper()
        self.db = self.db_helper.set_up()

    def tearDown(self) -> None:
        self.db_helper.tear_down()
