from sqlalchemy import create_engine, text, func, and_
from working_with_the_database.table_models import *
from miscellaneous_data.сommon_words import *
from miscellaneous_data.env_data import *
from sqlalchemy.orm import sessionmaker
import random as rand
import sqlalchemy


# Назначение DSN
DSN = f"postgresql://{DB_LOGIN}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"


# Функция создания сформированных таблиц
def create_tables(engine):
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    print("Таблицы common_word, users и users_words были созданы и отчищены")  # Полу-логирование


# Создание БД
try:
    engine_creator = create_engine(f"postgresql://{DB_LOGIN}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}")
    with engine_creator.connect() as connect:
        connect.execute(text("COMMIT"))
        connect.execute(text('CREATE DATABASE users_words_db'))
    print("База данных 'users_words_db' была создана")  # Полу-логирование
except sqlalchemy.exc.ProgrammingError:
    print("База данных уже существует - можно работать")  # Полу-логирование
except Exception as e:
    raise e("Фатальная ошибка исполнения кода")

# Создание инструментов и движка
engine = create_engine(DSN)

create_tables(engine)

Session = sessionmaker(bind=engine)

# Добавление общих слов
with Session() as session:
    for word, translated in common_words.items():
        session.add(CommonWordsBase(word=word, translated=translated))
    session.commit()


def get_random_translation(user_id):
    """
    Возвращает случайный перевод слова
    Если у пользователя есть добавленные слова, то может вернуть перевод из них
    """
    with Session() as session:
        translated_common = session.query(CommonWordsBase.translated).all()
        translated_user = session.query(WordBase.translated).filter(WordBase.affiliation == user_id).all()
        all_translated = translated_user + translated_common
        return rand.choice(all_translated)[0]


def get_random_word(user_id):
    """
    Возвращает случайное слово из общего словаря
    Если у пользователя есть добавленные слова, то может вернуть слово из них
    """
    with Session() as session:
        words_common = session.query(CommonWordsBase.word).all()
        words_user = session.query(WordBase.word).filter(WordBase.affiliation == user_id).all()
        all_words = words_user + words_common
        return rand.choice(all_words)[0]


def get_translated_word(search):
    """
    Получение перевода для слова
    """
    if search in common_words.keys():
        return common_words.get(search)
    else:
        with Session() as session:
            query = session.query(WordBase.translated)
            query = query.filter(WordBase.word == search).first()
            return query[0]


def get_a_word_on_translation(search):
    """
    Возвращает слово по переданному переводу
    """
    if search in common_words.values():
        for сouple in common_words.items():
            if search in сouple:
                return сouple[0]

    else:
        with Session() as session:
            query = session.query(WordBase.word)
            query = query.filter(WordBase.translated == search).first()
            return query[0]


def check_for_word(message):
    """
    Проверка наличия слова у пользователя
    """
    with Session() as session:
        check = session.query(WordBase.word)
        check = check.filter(and_(WordBase.word == message.text, WordBase.affiliation == message.from_user.id)).all()
        return check


def word_count(message):
    """
    Подсчет количества доступных слов у пользователя
    """
    with Session() as session:
        count = session.query(func.count(WordBase.word).filter(WordBase.affiliation == message.from_user.id)).all()
        return count[0][0]


def add_user(message):
    """
    Добавление пользователя при начале взаимодействия
    """
    with Session() as session:
        session.add(UsersBase(
            user_id=message.from_user.id,
            current_translate='',
            added_word='',
            successful_counter=0,
            laziness_counter=0,
            failure_counter=0
        )
        )
        session.commit()


def changing_user_settings(
        message,
        added_word: str = None,
        current_translate: str = None,
        successful_counter: int = None,
        failure_counter: int = None,
        laziness_counter: int = None
):
    """
    Изменение переданного параметра у пользователя
    """
    if added_word is not None:
        with Session() as session:
            session.query(UsersBase).filter(UsersBase.user_id == message.from_user.id).update(
                {'added_word': added_word})
            session.commit()

    if current_translate is not None:
        with Session() as session:
            session.query(UsersBase).filter(UsersBase.user_id == message.from_user.id).update(
                {'current_translate': current_translate})
            session.commit()

    if successful_counter is not None:
        with Session() as session:
            session.query(UsersBase).filter(UsersBase.user_id == message.from_user.id).update(
                {'successful_counter': successful_counter})
            session.commit()

    if failure_counter is not None:
        with Session() as session:
            session.query(UsersBase).filter(UsersBase.user_id == message.from_user.id).update(
                {'failure_counter': failure_counter})
            session.commit()

    if laziness_counter is not None:
        with Session() as session:
            session.query(UsersBase).filter(UsersBase.user_id == message.from_user.id).update(
                {'laziness_counter': laziness_counter})
            session.commit()

    return


def validate_user_settings(
        message,
        added_word=None,
        current_translate=None,
        successful_counter=None,
        failure_counter=None,
        laziness_counter=None
):
    """
    Выборка нужно параметра у пользователя
    """
    if added_word is not None:
        with Session() as session:
            word_added = session.query(UsersBase.added_word).filter(UsersBase.user_id == message.from_user.id).first()
            return word_added[0]

    if current_translate is not None:
        with Session() as session:
            translate_corrent = session.query(UsersBase.current_translate).filter(
                UsersBase.user_id == message.from_user.id).first()
            return translate_corrent[0]

    if successful_counter is not None:
        with Session() as session:
            result = session.query(UsersBase.successful_counter).filter(
                UsersBase.user_id == message.from_user.id).first()
            return result[0]

    if failure_counter is not None:
        with Session() as session:
            result = session.query(UsersBase.failure_counter).filter(UsersBase.user_id == message.from_user.id).first()
            return result[0]

    if laziness_counter is not None:
        with Session() as session:
            result = session.query(UsersBase.laziness_counter).filter(UsersBase.user_id == message.from_user.id).first()
            return result[0]

    return
