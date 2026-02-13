from sqlalchemy.orm import declarative_base, Mapped, mapped_column
from sqlalchemy import String, Integer, BigInteger, ForeignKey


# Назначение класса для наследования
Base = declarative_base()


# Создания класса-таблицы общих слов
class CommonWordsBase(Base):
    __tablename__ = 'common_words'

    word: Mapped[str] = mapped_column(String(155), primary_key=True)
    translated: Mapped[str] = mapped_column(String(155))

    def __repr__(self):
        return f"{self.word}"


# Создания класса-таблицы слов пользователей
class WordBase(Base):
    __tablename__ = 'words'

    word: Mapped[str] = mapped_column(String(155), unique=True)
    translated: Mapped[str] = mapped_column(String(155), primary_key=True, unique=True)
    affiliation: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.user_id", ondelete="CASCADE"))

    def __repr__(self):
        return f"{self.word}"


# Создания класса-таблицы пользователей
class UsersBase(Base):
    __tablename__ = 'users'

    user_id: Mapped[int] = mapped_column(BigInteger, unique=True, primary_key=True)
    current_translate: Mapped[str] = mapped_column(String(155))
    added_word: Mapped[str] = mapped_column(String(155))
    successful_counter: Mapped[int] = mapped_column(Integer)
    laziness_counter: Mapped[int] = mapped_column(Integer)
    failure_counter: Mapped[int] = mapped_column(Integer)