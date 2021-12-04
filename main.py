#Импорт необходимых библиотек
import telebot
from pymongo import MongoClient
from telebot import types
import config
import strings
import register

bot = telebot.TeleBot(config.TESTTOKEN)


class DataBase: #Класс для базы данных пользователей бота
    def __init__(self): #Метод вызывается при инициации класса
        cluster = MongoClient(congig.clusterURL) #Подклчение к Mongo-клиенту

        self.db = cluster["SecuTor"] #Инициация кластера из MongoBD
        self.users = self.db["SecuTor"] #Инициация коллекции из MongoBD

    def get_user(self, message):
        from_user = message.from_user
        user = self.users.find_one({"user_id": from_user.id})

        if user: #Проверка на наличие записи о пользователе в БД
            return user #Если есть - возвращаем имеющуюся запись

        else: #Если записи нет - создаём новую
            user = {
                "user_id": from_user.id,
                "first_name": from_user.first_name,
                "last_name": from_user.last_name,
                "knowledge": {strings.passwordsAndLogins: 0, strings.webAndInternet: 0, strings.computerSafety: 0}
            }

            self.users.insert_one(user)

            return user


db = DataBase() #Инициация объекта базы данных


@bot.message_handler(commands=['start']) #Функция, вызываемая при команде /start
def start_message(message):
    user = db.get_user(message)

    bot.send_message(message.chat.id, ('Привет, ' + message.from_user.first_name + '!')) #Фтправка приветственного сообщения пользователю
    bot.send_message(message.chat.id, strings.initialization)

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True) #Фткрытие начального меню для работы с ботом
    menu_one = types.KeyboardButton(strings.start_message)
    markup.add(menu_one)
    bot.send_message(user["user_id"], strings.userFound, reply_markup=markup)


def open_main_menu(message): #Функция для открытия главного меню бота
    markup = types.ReplyKeyboardMarkup(row_width=1)
    menu_one = types.InlineKeyboardButton(strings.test, callback_data='primaryTest')
    menu_two = types.InlineKeyboardButton(strings.regTraining, callback_data='training')
    menu_three = types.InlineKeyboardButton(strings.begin, callback_data='startEducation')

    markup.add(menu_one, menu_two, menu_three)

    bot.send_message(message.chat.id, strings.greetings, reply_markup=markup)


@bot.message_handler(commands=['help']) #Функция, вызываемая при команде /help
def get_help(message):
    bot.send_message(message.chat.id, strings.helpString)


@bot.message_handler(content_types=['text']) #Функция ответчика на сообщения пользователя
def get_text_messages(message):
    content = message.text #Текст сообщения пользователя

    if content == strings.start_message:
        open_main_menu(message)
    elif content == strings.regTraining:
        register.register_procedure(bot, message)  # Отлов кейса при выборе тренинга
    elif content == strings.backToMenu:
        open_main_menu(message)  # Отлов кейса при возврате в главное меню
    else:
        bot.send_message(message.chat.id, strings.unsignedMessage)  # Отправка сообщения что бот не знает что ответить при недетерминированных кейсах


bot.polling(none_stop=True, interval=0)
