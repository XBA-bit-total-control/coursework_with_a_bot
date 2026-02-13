from working_with_the_bot.resolution_of_appeals import add_user, start_class, admin
from working_with_the_bot.creating_a_bot import bot
import sqlalchemy.exc


# Обработчик запуска бота
@bot.message_handler(commands=['start', "старт"])
def greetings(message):
    try:
        add_user(message)
        if message.from_user.last_name is None:
            bot.send_message(
                message.chat.id,
                f"""Здравствуй {message.from_user.first_name}!
Я помогу тебе в изучении английского языка
Чтобы начать занятие напиши /start_class"""
            )
        else:
            bot.send_message(
                message.chat.id,
                f"""Здравствуй {message.from_user.first_name} {message.from_user.last_name}!
Я помогу тебе в изучении английского языка
Чтобы начать занятие напиши /start_class"""
            )
    except sqlalchemy.exc.IntegrityError:
        bot.send_message(
            message.chat.id,
            "Вы уже можете начать заниматься"
        )


# Обработка команд после /start
@bot.message_handler(commands=['start_class', 'начать_занятие'])
def start_class_com(message):
    try:
        start_class(message)
    except TypeError:
        greetings(message)


@bot.message_handler(commands=['admin'])
def become_an_admin(message):
    bot.send_message(
        message.chat.id,
        'Введите пароль:',
    )
    bot.register_next_step_handler(message, admin)