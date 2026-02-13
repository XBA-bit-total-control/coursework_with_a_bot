from working_with_the_bot.processing_of_requests import bot


# Запуск программы
if __name__ == '__main__':
    print("Бот был запущен")
    bot.polling()
    print("Бот отключен")