from working_with_the_database.database_operations import *
from miscellaneous_data.buttons_when_editing import *
from working_with_the_bot.creating_a_bot import bot
from miscellaneous_data.answer_options import *
from telebot.types import ReplyKeyboardMarkup
from telebot import TeleBot, types
from random import shuffle, choice
import webbrowser
import os


def random_buttons(message, repeat=False):
    """
    Создание случайных кнопок для вариантов ответа пользователя
    """

    def random_word_sheet():
        """
        Заполнение списка вариантами ответов
        """
        while len(current_translations) < 4:
            word = get_random_translation(message.from_user.id)
            if word not in current_translations:
                current_translations.append(word)

    # Получаем случайный перевод
    if repeat:
        # Получение текущего перевода у пользователя
        current_translate = validate_user_settings(message, current_translate=True)
        # Получение случайного слова
        random_word = get_a_word_on_translation(current_translate)
        # Формирование списка вариантов ответов
        current_translations = [current_translate]
        random_word_sheet()

    else:
        # Выбор рандомного слова и его перевода
        random_word = get_random_word(message.from_user.id)
        random_transfer = get_translated_word(random_word)

        # Взятие текущего перевода у пользователя
        current_translate = validate_user_settings(message, current_translate=True)

        # Подбираем слово, которое не использовалось в прошлый раз
        while random_transfer == current_translate:
            random_word = get_random_word(message.from_user.id)
            random_transfer = get_translated_word(random_word)
        else:
            changing_user_settings(message, current_translate=random_transfer)

        # Формирование списка вариантов ответов
        current_translations = [random_transfer]
        random_word_sheet()

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

    return [random_word, marcup]


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
                        changing_user_settings(message, added_word=sms[0])
                        session.add(WordBase(
                            affiliation=message.from_user.id,
                            word=sms[0],
                            translated=sms[1])
                        )
                        session.commit()

                        bot.send_message(
                            message.chat.id,
                            f"Слово '{sms[0]}' добавлено вам в изучаемые \n"
                            f"Сейчас у вам всего [ {word_count(message) + 10} ] слов для занятий",
                            reply_markup=buttons_when_editing
                        )
                        bot.register_next_step_handler(message, reply_after_adding)
                        return

                # Обработка не верного ввода
                else:
                    bot.send_message(
                        message.chat.id,
                        "То что вы ввели не подойдет для добавления",
                        reply_markup=buttons_when_editing
                    )
                    bot.register_next_step_handler(message, reply_after_adding)
                    return
            else:
                bot.send_message(
                    message.chat.id,
                    "То что вы ввели не подойдет для добавления",
                    reply_markup=buttons_when_editing
                )
                bot.register_next_step_handler(message, reply_after_adding)
                return

        # Обработка ошибок
        except IndexError:
            bot.send_message(
                message.chat.id,
                """Слово не получилось добавить из-за того что вы ввели его не в том формате
Повторите попытку корректно""",
                reply_markup=buttons_when_editing
            )
            bot.register_next_step_handler(message, reply_after_adding)

        except AttributeError:
            bot.send_message(
                message.chat.id,
                """Слово не получилось добавить из-за того что был передан не верный тип сообщения
Повторите попытку корректно""",
                reply_markup=buttons_when_editing
            )
            bot.register_next_step_handler(message, reply_after_adding)

        except sqlalchemy.exc.IntegrityError:
            bot.send_message(
                message.chat.id,
                f"Слово '{sms[0]}' уже есть в у вас в изучаемых",
                reply_markup=buttons_when_editing
            )
            bot.register_next_step_handler(message, reply_after_adding)

        except Exception as error:
            bot.send_message(
                message.chat.id,
                f"""Слово не получилось добавить из-за ошибки {error}
Повторите попытку корректно""",
                reply_markup=buttons_when_editing
            )
            bot.register_next_step_handler(message, reply_after_adding)


def delete_word(message):
    """
    Удаляет слово из базы данных для обращающегося пользователя
    """

    def d_w(removable):
        """
        Подфункция для сокращения кода
        """

        with Session() as session:
            session.query(WordBase).filter(WordBase.word == removable).delete()
            session.commit()

        if removable == validate_user_settings(message, added_word=True):
            bot.send_message(
                message.chat.id,
                "Прошлое добавленное вами слово удаленно",
                reply_markup=buttons_when_editing
            )
            changing_user_settings(message, added_word='')

        else:
            bot.send_message(
                message.chat.id,
                f"Слово '{removable}' было удалено из вашего обучения",
                reply_markup=buttons_when_editing
            )

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
            reply_markup=buttons_when_editing
        )
        bot.register_next_step_handler(message, reply_after_adding)
        return

    elif message.text == "Отменить добавление прошлого слова 🔙":
        added_word = validate_user_settings(message, added_word=True)
        if added_word == '':
            bot.send_message(
                message.chat.id,
                "Сейчас отменять вам и нечего",
                reply_markup=buttons_when_editing
            )
            bot.register_next_step_handler(message, reply_after_adding)
            return
        else:
            d_w(added_word)
            return

    elif check_for_word(message) == []:
        bot.send_message(
            message.chat.id,
            "Такого слова у вас в изучаемых нет",
            reply_markup=buttons_when_editing
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

    # Получение случайных кнопок и слова
    buttons = random_buttons(message)

    bot.send_message(
        message.chat.id,
        f"Какой будет перевод у слова   ->  {buttons[0]}",
        reply_markup=buttons[1]
    )
    bot.register_next_step_handler(message, reply_to_press)


def add_word_to_user(message):
    """
    Промежуточная функция-вопрос для добавления слова
    """
    bot.send_message(
        message.chat.id,
        """
        Введите пожалуйста сообщение вида:
                 слово перевод
        """,
        reply_markup=buttons_when_editing
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
        reply_markup=buttons_when_editing
    )
    bot.register_next_step_handler(message, delete_word)


def reply_to_press(message):
    """
    Обработчик ответа пользователя на занятии
    """
    # Получение счетчиков пользователя
    successful_counter = validate_user_settings(message, successful_counter=True)
    failure_counter = validate_user_settings(message, failure_counter=True)
    laziness_counter = validate_user_settings(message, laziness_counter=True)

    # Обработка успешного ответа
    if message.text == validate_user_settings(message, current_translate=True):
        if successful_counter == 4:  # Поощрение за 5 правильных ответов подряд
            bot.send_message(message.chat.id, choice(praise))
            changing_user_settings(
                message,
                successful_counter=0,
                failure_counter=0,
                laziness_counter=0
            )
            start_class(message)
        else:
            bot.send_message(message.chat.id, choice(successful_responses))
            changing_user_settings(
                message,
                successful_counter=successful_counter + 1,
                failure_counter=0,
                laziness_counter=0
            )
            start_class(message)

    # Активация пропуска слова
    elif message.text == "Пропустить ❌️":
        if laziness_counter == 7:  # Ограничение на пропуск
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
            changing_user_settings(
                message,
                laziness_counter=laziness_counter + 1,
            )
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
            reply_markup=random_buttons(message, repeat=True)[1]
        )
        bot.register_next_step_handler(message, reply_to_press)

    # Ловушка
    elif message.text == "/admin":
        become_an_admin(message)

    # Обработка при неправильном ответе
    else:
        if failure_counter == 3:
            bot.send_message(message.chat.id, choice(dead_end))
            changing_user_settings(
                message,
                successful_counter=0,
                failure_counter=0,
                laziness_counter=0
            )
            start_class(message)  # Автоматический пропуск слова при частых ошибках
        else:
            bot.send_message(
                message.chat.id,
                choice(unsuccessful_answers),
                reply_markup=random_buttons(message, repeat=True)[1]
            )
            changing_user_settings(
                message,
                successful_counter=0,
                failure_counter=failure_counter + 1
            )
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
        if validate_user_settings(message, added_word=True) == '':
            bot.send_message(
                message.chat.id,
                "Сейчас отменять вам и нечего",
                reply_markup=buttons_when_editing
            )
            bot.register_next_step_handler(message, reply_after_adding)
        else:
            delete_word(message)
            bot.register_next_step_handler(message, reply_after_adding)


    elif message.text == "Продолжить занятие ✅":
        start_class(message)

    elif message.text == "/admin":
        become_an_admin(message)

    # При незафиксированном вводе
    else:
        bot.send_message(
            message.chat.id,
            choice(incorrect_input),
            reply_markup=buttons_when_editing
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


def become_an_admin(message):
    bot.send_message(
        message.chat.id,
        'Введите пароль:',
    )
    bot.register_next_step_handler(message, admin)
