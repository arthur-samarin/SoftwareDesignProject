from app.bot import templates, buttons
from test.bot import AppTestCase


class TestBasicCommands(AppTestCase):
    def setUp(self):
        self.set_up_app()

    def tearDown(self) -> None:
        self.tear_down_app()

    def test_start(self):
        self.assert_has_answer('/start', templates.start_message)

    def test_about(self):
        self.assert_has_answer(buttons.button_about, templates.about_bot)

    def test_unknown_command(self):
        self.assert_has_answer('1u133os8wo', templates.main_message)
