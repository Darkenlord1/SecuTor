# Импорт необходимых библиотек
from telebot import types
import strings
import config
import register


def open_user_info(bot, message):
    markup = types.ReplyKeyboardMarkup(row_width=1)
    menu_one = types.InlineKeyboardButton(strings.show_requests)
    menu_two = types.InlineKeyboardButton(strings.show_info)
    menu_three = types.InlineKeyboardButton(strings.sertificate)
    back = types.InlineKeyboardButton(strings.backToMenu, callback_data='back')

    markup.add(menu_one, menu_two, menu_three, back)
    bot.send_message(message.chat.id, strings.choice_item, reply_markup=markup)


def get_requests(bot, message):
    all_requests = register.get_requests(message)

    if all_requests != '':
        bot.send_message(message.chat.id, (strings.requests_found + '\n' + str(all_requests)))
    else:
        bot.send_message(message.chat.id, strings.requests_not_found)


def get_user_info(bot, message, user):
    user_knowledge = user["knowledge"]

    user_info = user["first_name"] + ', ' + strings.user_info_text + strings.completed_trainings + '"' + strings.passwordsAndLogins + '":  ' + str(user_knowledge[strings.passwordsAndLogins]) + strings.info_completion
    user_info += '\n' + strings.completed_trainings + '"' + strings.webAndInternet + '":  ' + str(user_knowledge[strings.webAndInternet]) + strings.info_completion
    user_info += '\n' + strings.completed_trainings + '"' + strings.computerSafety + '":  ' + str(user_knowledge[strings.computerSafety]) + strings.info_completion

    bot.send_message(message.chat.id, user_info)
