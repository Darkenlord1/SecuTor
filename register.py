#Импорт необходимых библиотек
from telebot import types
import strings

def registerProcedure(bot, message):
    markup = types.ReplyKeyboardMarkup(row_width=3)

    theme1 = types.InlineKeyboardButton(strings.passwordsAndLogins, callback_data='theme1')
    theme2 = types.InlineKeyboardButton(strings.webAndInternet, callback_data='theme2')
    theme3 = types.InlineKeyboardButton(strings.computerSafety, callback_data='theme3')
    back = types.InlineKeyboardButton(strings.backToMenu, callback_data='backToMenu')

    markup.add(theme1, theme2, theme3, back) #Меню выбора темы тренинга и кнопки выхода в главное меню
    bot.send_message(message.chat.id, strings.regTrainingDialog, reply_markup=markup) #Вывод сообщения с меню
