# Импорт необходимых библиотек
from telebot import types
import strings


def register_procedure(bot, message):
    markup = types.ReplyKeyboardMarkup(row_width=1)

    theme1 = types.InlineKeyboardButton(strings.passwordsAndLogins)
    theme2 = types.InlineKeyboardButton(strings.webAndInternet)
    theme3 = types.InlineKeyboardButton(strings.computerSafety)
    back = types.InlineKeyboardButton(strings.backToMenu)

    markup.add(theme1, theme2, theme3, back)  # Меню выбора темы тренинга и кнопки выхода в главное меню
    bot.send_message(message.chat.id, strings.regTrainingDialog, reply_markup=markup)  # Вывод сообщения с меню
