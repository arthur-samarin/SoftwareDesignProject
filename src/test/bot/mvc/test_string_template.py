from unittest import TestCase

from app.bot.mvc import Template


class TestStringFormatTemplate(TestCase):
    def test(self):
        template = Template.from_string_format('{greeting}, {name}!', buttons=[['A']])
        content = template.create_message({
            'greeting': 'Hello', 'name': 'world'
        })
        self.assertEqual(content.text, 'Hello, world!')
        self.assertEqual(content.buttons, [['A']])
