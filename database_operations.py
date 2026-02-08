from sqlalchemy import create_engine, func, text, func, and_, or_
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from table_models import *
import sqlalchemy
import os



# Назначение общих слов всех пользователей
common_words = {
    "bubble": "пузырь",
    "red": "красный",
    "he": "он",
    "silk": "шелк",
    "giraffe": "жираф",
    "bread": "хлеб",
    "pillow": "подушка",
    "car": "машина",
    "waffle": "вафля",
    "cat": "кошка",
    "lesson": "урок"
}

# Чтение и запись .env данных
load_dotenv()

db_login = os.getenv("DB_LOGIN")
db_password = os.getenv("DB_PASSWORD")
db_host = os.getenv("DB_HOST")
db_port = os.getenv("DB_PORT")
db_name = os.getenv("DB_NAME")

# Непосредственно работа с БД
DSN = f"postgresql://{db_login}:{db_password}@{db_host}:{db_port}/{db_name}"

# Создание БД
try:
    engine_creator = create_engine(f"postgresql://{db_login}:{db_password}@{db_host}:{db_port}")
    with engine_creator.connect() as connect:
        connect.execute(text("COMMIT"))
        connect.execute(text('CREATE DATABASE users_words_db'))
    print("База данных 'users_words_db' была создана")    # Полу-логирование
except sqlalchemy.exc.ProgrammingError:
    print("База данных уже существует - можно работать")    # Полу-логирование
except Exception as e:
    raise e("Фатальная ошибка исполнения кода")

# Функция создания сформированных таблиц
def create_tables(engine):
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    print("Таблицы common_word, users и users_words были созданы и отчищены")    # Полу-логирование


# Создание инструментов и движка
engine = create_engine(DSN)

create_tables(engine)

Session = sessionmaker(bind=engine)

# Добавление общих слов
with Session() as session:
    session.add(UsersBase(user_id=100))
    session.commit()
    for translated, word in common_words.items():
        session.add(WordBase(word=word, translated=translated, affiliation=100))
    session.commit()


def get_random_translation(user_id):
    """
    Возвращает случайный перевод слова
    Если у пользователя есть добавленные слова, то может вернуть перевод из них
    """
    with Session() as session:
        word_from_func = session.query(WordBase.translated).filter(
            or_(WordBase.affiliation == 100, WordBase.affiliation == user_id)).order_by(
            func.random()).limit(1).first()
        return word_from_func[0]


def get_random_word(user_id):
    """
    Возвращает случайное слово из общего словаря
    Если у пользователя есть добавленные слова, то может вернуть слово из них
    """
    with Session() as session:
        word_from_func = session.query(WordBase.word).filter(
            or_(WordBase.affiliation == 100, WordBase.affiliation == user_id)).order_by(
            func.random()).limit(1).first()
        return word_from_func[0]


def get_translated_word(search):
    """
    Получение перевода для слова
    """
    with Session() as session:
        translated_from_func = session.query(WordBase.word).filter(WordBase.translated == search).first()
        return translated_from_func[0]


def check_for_word(message):
    """
    Проверка наличия слова как у пользователя, так и общего
    """
    with Session() as session:
        check = session.query(WordBase.word).filter(and_(WordBase.translated == message.text, WordBase.affiliation == message.from_user.id)).all()
        return check


def word_count(message):
    """
    Подсчет количества доступных слов у пользователя
    """
    with Session() as session:
        count =  session.query(func.count(WordBase.word).filter(WordBase.affiliation == message.from_user.id)).all()
        return count[0][0]


def add_user(message):
    """
    Добавление пользователя при начале взаимодействия
    """
    with Session() as session:
        try:
            session.add(UsersBase(user_id=message.from_user.id))
            session.commit()
            return
        except sqlalchemy.exc.IntegrityError:
            session.rollback()