from telebot import types


# Назначение кнопок при редактировании
buttons_when_editing = types.ReplyKeyboardMarkup()
buttons_when_editing.row(
    types.KeyboardButton("Добавить слово ✏️"),
    types.KeyboardButton("Удалить слово ️🚫")
)
buttons_when_editing.row(
    types.KeyboardButton("Отменить добавление прошлого слова 🔙")
)
buttons_when_editing.row(
    types.KeyboardButton("Продолжить занятие ✅")
)