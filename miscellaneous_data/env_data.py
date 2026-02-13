from dotenv import load_dotenv
import os


load_dotenv()

# Получение переменных окружения
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_LOGIN = os.getenv("DB_LOGIN")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
TOKEN = os.getenv("TOKEN")