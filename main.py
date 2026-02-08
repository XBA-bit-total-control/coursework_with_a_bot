from telebot.types import ReplyKeyboardMarkup
from telebot import TeleBot, types
from random import shuffle, choice
from database_operations import *
from dotenv import load_dotenv
import webbrowser
import telebot
import os



# Читаем и запоминаем токен
load_dotenv()
TOKEN = os.getenv("TOKEN")

bot = telebot.TeleBot(TOKEN)

# Назначение общих переменных
marcup = ''
added_word = ''
current_translate = ''

# Назначение счётчиков
failure_counter = 0
laziness_counter = 0
successful_counter = 0

# Успешные ответы для пользователя
successful_responses = [
    "Правильно!",
    "Все верно!",
    "Successfully!",
    "Твой ответ верный",
    "Хорошо - правильно",
    "Ты ответил правильно",
    "Ответ принят - все верно",
    "Это был правильный ответ",
]

# Похвальные ответы
praise = [
    "Совершенно верно! Ты многому обучен",
    "Молодец! Хорошо английский знаешь 👍",
    "Замечательные ответы - перевод верный"
]

# Неуспешные ответы
unsuccessful_answers = [
    "Не верно",
    "Неправильно",
    "Перевод выбран не верно",
    "Не верно - ответь ещё раз",
    "Неправильно - попробуй заново",
    "Ты ответил не верно - попробуй ещё раз",
    "Ответ не правильный - выбери верный перевод"
]

# Ответы при слишком большом количестве ошибок
dead_end = [
    "Понимаю слово сложное - меняем слово",
    "Вовсе не правильно. Давай другое слово",
    "Возможно ты такого совсем не знаешь - держи другое",
    "Эх дружок совсем не правильно. Вот тебе другое слово",
]

# Ответы при некорректном вводе
incorrect_input = [
    "Мы такого не знаем",
    "Я такого не понимаю",
    "Моя твоя не понимать",
    "Команда не распознана",
    "Не понимаю что ты хочешь",
    "Я не знаю чего ты от меня хочешь",
    "То что ты написал не распознаётся",
    "Я пока не знаю что и ответить на это",
]

# Назначение кнопок редактирования
buttons_when_adding = types.ReplyKeyboardMarkup()
buttons_when_adding.row(
    types.KeyboardButton("Добавить слово ✏️"),
    types.KeyboardButton("Удалить слово ️🚫")
)
buttons_when_adding.row(
    types.KeyboardButton("Отменить добавление прошлого слова 🔙")
)
buttons_when_adding.row(
    types.KeyboardButton("Продолжить занятие ✅")
)


# Обработчик запуска бота
@bot.message_handler(commands=['start', "старт"])
def greetings(message):
    bot.send_message(
        message.chat.id,
        f"""Здравствуй {message.from_user.first_name} {message.from_user.last_name}!
Я помогу тебе в изучении английского языка
Чтобы начать занятие напиши /start_class"""
    )
    add_user(message)


def add_word_user(message):
    """
    Позволяет добавить слово в базу данных для конкретного пользователя
    """
    if message.text == "Добавить слово ✏️":
        bot.send_message(
            message.chat.id,
            """
            Нужно вам ввести слова в формате:
            слово[EN] перевод[RU]
Или нажмите 'Продолжить занятие ✅'
            """
        )
        bot.register_next_step_handler(message, add_word_user)

    elif message.text == "Удалить слово ️🚫":
        delete_word_to_user(message)

    elif message.text == "Отменить добавление прошлого слова 🔙":
        bot.send_message(
            message.chat.id,
            """
            Сейчас отменить добавленное слово не выйдет
Если хотите добавить слово, то введите его в нужном формате
Или выберите 'Продолжить занятие ✅'
            """
        )
        bot.register_next_step_handler(message, add_word_user)

    elif message.text == "Продолжить занятие ✅" or message.text == "/start_class":
        start_class(message)

    elif message.text == "/admin":
        become_an_admin(message)

    else:
        try:
            # Махинации над проверкой и редактированием поступивших слов
            global added_word
            sms = message.text.lower()

            for let in sms:
                if ord(let) in range(97, 123) or ord(let) in range(1072, 1104) or ord(let) == 32:
                    pass
                else:
                    sms = sms.replace(let, "")

            sms = sms.split()

            for ind, el in enumerate(sms):
                sms[ind] = sms[ind].replace(" ", "")

            if len(sms) == 2:
                if sms[0] != "" and sms[1] != "":
                    with Session() as session:
                        added_word = sms[0]
                        session.add(WordBase(
                            affiliation=message.from_user.id,
                            word=sms[1],
                            translated=sms[0])
                        )
                        session.commit()

                        bot.send_message(
                            message.chat.id,
                            f"Слово '{sms[0]}' добавлено вам в изучаемые \n"
                            f"Сейчас у вам всего [ {word_count(message) + 10} ] слов для занятий",
                            reply_markup=buttons_when_adding
                        )
                        bot.register_next_step_handler(message, reply_after_adding)
                        return

                # Обработка не верного ввода
                else:
                    bot.send_message(
                        message.chat.id,
                        "То что вы ввели не подойдет для добавления",
                        reply_markup=buttons_when_adding
                    )
                    bot.register_next_step_handler(message, reply_after_adding)
                    return
            else:
                bot.send_message(
                    message.chat.id,
                    "То что вы ввели не подойдет для добавления",
                    reply_markup=buttons_when_adding
                )
                bot.register_next_step_handler(message, reply_after_adding)
                return

        # Обработка ошибок
        except IndexError:
            bot.send_message(
                message.chat.id,
                f"Слово не получилось добавить из-за того что вы ввели его не в том формате",
                reply_markup=buttons_when_adding
            )
            bot.register_next_step_handler(message, reply_after_adding)

        except AttributeError:
            bot.send_message(
                message.chat.id,
                f"Слово не получилось добавить из-за того что был передан не верный тип сообщения",
                reply_markup=buttons_when_adding
            )
            bot.register_next_step_handler(message, reply_after_adding)

        except sqlalchemy.exc.IntegrityError:
            bot.send_message(
                message.chat.id,
                f"Слово '{sms[0]}' уже есть в изучаемых по умолчанию",
                reply_markup=buttons_when_adding
            )
            bot.register_next_step_handler(message, reply_after_adding)

        except Exception as error:
            bot.send_message(
                message.chat.id,
                f"Слово не получилось добавить из-за ошибки {error}",
                reply_markup=buttons_when_adding
            )
            bot.register_next_step_handler(message, reply_after_adding)


def delete_word(message):
    """
    Удаляет слово из базы данных для обращающегося пользователя
    """
    global added_word

    def d_w(removable):
        """
        Подфункция для сокращения кода
        """
        global added_word

        with engine.connect() as connect:
            connect.execute(text(f"DELETE FROM words WHERE translated = '{removable}' AND affiliation = {message.from_user.id}"))
            connect.execute(text("COMMIT"))

        if removable == added_word:
            bot.send_message(
                message.chat.id,
                "Прошлое добавленное вами слово удаленно",
                reply_markup=buttons_when_adding
            )
            added_word = ''

        else:
            bot.send_message(
                message.chat.id,
                f"Слово '{removable}' было удалено из вашего обучения",
                reply_markup=buttons_when_adding
            )

        bot.register_next_step_handler(message, reply_after_adding)
        return

    # Проверка поступивших данных
    if message.text == "Добавить слово ✏️":
        bot.send_message(
            message.chat.id,
            """
            Этого сделать сейчас не получится
Введите пожалуйста слово которое хотите удалить:
Или выберите 'Продолжить занятие ✅'
            """
        )
        bot.register_next_step_handler(message, delete_word)

    elif message.text == "Удалить слово ️🚫":
        bot.send_message(
            message.chat.id,
            "Введите слово для удаления:"
        )
        bot.register_next_step_handler(message, delete_word)

    elif message.text == "Продолжить занятие ✅":
        start_class(message)

    elif message.text == "/start_class":
        start_class(message)

    elif message.text == "/admin":
        become_an_admin(message)

    elif message.text in common_words.keys():
        bot.send_message(
            message.chat.id,
            "Это общее слово удалить его вам нельзя",
            reply_markup=buttons_when_adding
        )
        bot.register_next_step_handler(message, reply_after_adding)
        return

    elif message.text == "Отменить добавление прошлого слова 🔙":
        if added_word == '':
            bot.send_message(
                message.chat.id,
                "Сейчас отменять вам и нечего",
                reply_markup=buttons_when_adding
            )
            bot.register_next_step_handler(message, reply_after_adding)
        else:
            d_w(added_word)
        return

    elif check_for_word(message) == []:
        bot.send_message(
            message.chat.id,
            "Такого слова у вас в изучаемых нет",
            reply_markup=buttons_when_adding
            )
        bot.register_next_step_handler(message, reply_after_adding)
        return

    else:
        d_w(message.text)
        bot.register_next_step_handler(message, reply_after_adding)
        return


def start_class(message):
    """
    Функция для запуска занятия
    """
    global current_translate, marcup

    # Получаем случайный перевод
    current_word = get_random_translation(message.from_user.id)

    # Подбираем слово, которое не использовалось в прошлый раз
    while current_translate == get_translated_word(current_word):
        current_word = get_random_translation(message.from_user.id)
    else:
        current_translate = get_translated_word(current_word)

    current_translations = [current_translate]

    # Подбираем случайные слова для вариантов ответа
    while len(current_translations) < 4:
        word = get_random_word(message.from_user.id)
        if word not in current_translations:
            current_translations.append(word)

    # Путаем порядок слов
    shuffle(current_translations)

    # Назначаем кнопки
    marcup = types.ReplyKeyboardMarkup()

    # Кнопки вариантов ответов
    button_1_row_1 = types.KeyboardButton(current_translations[0])
    button_2_row_1 = types.KeyboardButton(current_translations[1])
    button_3_row_2 = types.KeyboardButton(current_translations[2])
    button_4_row_2 = types.KeyboardButton(current_translations[3])

    # Постоянные кнопки управления
    button_5_row_3 = types.KeyboardButton("Пропустить ❌️")
    button_6_row_3 = types.KeyboardButton("Добавить слово ➕")
    button_7_row_4 = types.KeyboardButton("Удалить слово 🗑️")

    # Распределение кнопок по строкам
    marcup.row(button_1_row_1, button_2_row_1)
    marcup.row(button_3_row_2, button_4_row_2)
    marcup.row(button_5_row_3, button_6_row_3)
    marcup.row(button_7_row_4)

    bot.send_message(
        message.chat.id,
        f"Какой будет перевод у слова   ->  {current_word}",
        reply_markup=marcup
    )
    bot.register_next_step_handler(message, reply_to_press)


def add_word_to_user(message):
    """
    Промежуточная функция-вопрос добавления слова
    """
    bot.send_message(
        message.chat.id,
        """
        Введите пожалуйста сообщение вида:
                 слово перевод
        """,
        reply_markup=buttons_when_adding
    )
    bot.register_next_step_handler(message, add_word_user)


def delete_word_to_user(message):
    """
    Функция-вопрос для удаления слова
    """
    bot.send_message(
        message.chat.id,
        """
        Напишите какое слово удалить:
        """,
        reply_markup=buttons_when_adding
    )
    bot.register_next_step_handler(message, delete_word)


def reply_to_press(message):
    """
    Обработчик ответа пользователя на занятии
    """
    global successful_counter, failure_counter, laziness_counter

    # Успешный ответ
    if message.text == current_translate:
        if successful_counter == 5:     # Поощрение за 5 правильных ответов подряд
            bot.send_message(message.chat.id, choice(praise))
            successful_counter = 0
            laziness_counter = 0
            start_class(message)
        else:
            bot.send_message(message.chat.id, choice(successful_responses))
            successful_counter += 1
            laziness_counter = 0
            start_class(message)

    # Активация пропуска слова
    elif message.text == "Пропустить ❌️":
        if laziness_counter == 7:   # Ограничение на пропуск
            bot.send_message(
                message.chat.id,
                'Ты слишком много пропускаешь - это слово пропустить уже не получится. Попробуй ответить'
            )
            bot.register_next_step_handler(message, reply_to_press)
        else:
            bot.send_message(
                message.chat.id,
                'Хорошо - пропускаем слово'
            )
            laziness_counter +=1
            successful_counter = 0
            failure_counter = 0
            start_class(message)

    # Активация добавления слова
    elif message.text == "Добавить слово ➕":
        add_word_to_user(message)

    # Активация удаления слова
    elif message.text == "Удалить слово 🗑️":
        delete_word_to_user(message)

    # Если вдруг используется команда
    elif message.text == "/start_class":
        bot.send_message(
            message.chat.id,
            'Занятие уже идет',
            reply_markup = marcup
        )
        bot.register_next_step_handler(message, reply_to_press)

    # Ловушка
    elif message.text == "/admin":
        become_an_admin(message)

    # Неправильный ответ
    else:
        if failure_counter == 3:
            bot.send_message(message.chat.id, choice(dead_end))
            failure_counter = 0
            successful_counter = 0
            start_class(message)    # Автоматический пропуск слова при частых ошибках
        else:
            bot.send_message(
                message.chat.id,
                choice(unsuccessful_answers),
                reply_markup = marcup
            )
            failure_counter += 1
            bot.register_next_step_handler(message, reply_to_press)


def reply_after_adding(message):
    """
    Обработчик нажатий при редактировании
    """
    if message.text == "Добавить слово ✏️":
        add_word_to_user(message)

    elif message.text == "Удалить слово ️🚫":
        delete_word_to_user(message)

    elif message.text == "Отменить добавление прошлого слова 🔙":
        if added_word == '':
            bot.send_message(
                message.chat.id,
                "Сейчас отменять вам и нечего",
                reply_markup = buttons_when_adding
                )
            bot.register_next_step_handler(message, reply_after_adding)
        else:
            delete_word(message)

    elif message.text == "Продолжить занятие ✅":
        start_class(message)

    elif message.text == "/admin":
        become_an_admin(message)

    # При незафиксированном вводе
    else:
        bot.send_message(
            message.chat.id,
            choice(incorrect_input),
            reply_markup = buttons_when_adding
        )
        bot.register_next_step_handler(message, reply_after_adding)


def admin(message):
    try:
        if message.text == os.getenv("ADMIN"):
            bot.send_message(
                message.chat.id,
                'МОЛОДЕЦ)',
            )
        else:
            webbrowser.open('https://www.youtube.com/watch?v=dQw4w9WgXcQ&list=RDdQw4w9WgXcQ&start_radio=1')
    except:
        bot.send_message(
            message.chat.id,
            'У вас нет доступа',
        )


# Обработка команд после /start
@bot.message_handler(commands=['start_class', 'начать_занятие'])
def start_class_com(message):
    start_class(message)


@bot.message_handler(commands=['admin'])
def become_an_admin(message):
    bot.send_message(
        message.chat.id,
        'Введите пароль:',
    )
    bot.register_next_step_handler(message, admin)


# Запуск
if __name__ == '__main__':
    print("Бот был запущен")
    bot.polling()
    print("Бот отключен")