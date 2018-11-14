import unittest

from app.util.DiceRoller import DiceRoller


class DiceRollerTest(unittest.TestCase):
    def test_dice_roll_range(self):
        roller = DiceRoller()
        self.assertTrue(1 <= roller.roll() <= 6)
