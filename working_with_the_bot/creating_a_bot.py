from miscellaneous_data.env_data import TOKEN
from telebot import TeleBot, types
import telebot


# Вынесенное создание бота
bot = telebot.TeleBot(TOKEN)