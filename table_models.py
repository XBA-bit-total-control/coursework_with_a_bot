from sqlalchemy.orm import declarative_base, Mapped, mapped_column
from sqlalchemy import String, BigInteger, ForeignKey



# Назначение класса для наследования
Base = declarative_base()

# Создания класса-таблицы слов
class WordBase(Base):
    __tablename__ = 'words'

    word: Mapped[str] = mapped_column(String(155))
    translated: Mapped[str] = mapped_column(String(155), primary_key=True)
    affiliation: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.user_id", ondelete="CASCADE"))

    def __repr__(self):
        return f"{self.word}"


# Создания класса-таблицы пользователей
class UsersBase(Base):
    __tablename__ = 'users'

    user_id: Mapped[int] = mapped_column(BigInteger, unique=True, primary_key=True)


# Добавление и использование общих слов реализованны через пользователя с user_id = 100