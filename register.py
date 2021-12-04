# Импорт необходимых библиотек
from telebot import types
import strings
import config
from pymongo import MongoClient


class TrainingRequests:
    def __init__(self):
        cluster = MongoClient(config.clusterURL)  # Подклчение к Mongo-клиенту
        self.db = cluster["SecuTor"]  # Инициация кластера из MongoBD
        self.requests = self.db["Training_requests"]  # Инициация коллекции из MongoBD

    def create_request(self, message, direction):
        from_user = message.from_user
        user_request = self.requests.find_one({"user_id": from_user.id}, {"direction": direction})

        if user_request:
            request_status = strings.request_decline
            return request_status

        else:
            request = {
                "user_id": from_user.id,
                "username": from_user.username,
                "request_direction": direction,
                "request_status": True
            }

            self.requests.inset_one(request)
            request_status = strings.request_success

            return request_status


requests = TrainingRequests()


def register_procedure(bot, message):
    markup = types.ReplyKeyboardMarkup(row_width=1)

    theme1 = types.InlineKeyboardButton(strings.passwordsAndLogins, callback_data="passwordsAndLogins")
    theme2 = types.InlineKeyboardButton(strings.webAndInternet, callback_data="webAndInternet")
    theme3 = types.InlineKeyboardButton(strings.computerSafety, callback_data="computerSafety")
    back = types.InlineKeyboardButton(strings.backToMenu)

    markup.add(theme1, theme2, theme3, back)  # Меню выбора темы тренинга и кнопки выхода в главное меню
    bot.send_message(message.chat.id, strings.regTrainingDialog, reply_markup=markup)  # Вывод сообщения с меню


def create_new_request(message, direction):
    request = requests.create_request(message, direction)
    return request
