import app.bot.buttons as buttons

from app.bot.mvc import Template, MessageContent

start_message = Template.constant(MessageContent('''
Добро пожаловать, разработчик!

Здесь ты можешь показать всем свои навыки в разработке ИИ для пошаговых игр.
''', buttons.default_set))

about_bot = Template.constant(MessageContent('''
<b>❓ О боте</b>

Этот бот сделан в качесте проекта по курсу проектирования ПО.
''', buttons.default_set))
