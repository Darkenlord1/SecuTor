# Импорт необходимых библиотек
import telebot
from pymongo import MongoClient
from telebot import types
import config
import strings
import register
import user_profile
import certificates

bot = telebot.TeleBot(config.TESTTOKEN)


# Класс для базы данных пользователей бота
class DataBase:
    def __init__(self):  # Метод вызывается при инициации класса
        cluster = MongoClient(config.DBURL)  # Подклчение к Mongo-клиенту

        self.db = cluster["SecuTor"]  # Инициация кластера из MongoBD
        self.users = self.db["SecuTor"]  # Инициация коллекции из MongoBD

    def get_user(self, message):
        from_user = message.from_user
        user = self.users.find_one({"user_id": from_user.id})

        if user:  # Проверка на наличие записи о пользователе в БД
            return user  # Если есть - возвращаем имеющуюся запись

        else:  # Если записи нет - создаём новую
            user = {
                "user_id": from_user.id,
                "first_name": from_user.first_name,
                "last_name": from_user.last_name,
                "knowledge": {strings.passwordsAndLogins: 0, strings.webAndInternet: 0, strings.computerSafety: 0},
                "course_passed": False
            }

            self.users.insert_one(user)

            return user


db = DataBase()  # Инициация объекта базы данных


@bot.message_handler(commands=['start'])  # Функция, вызываемая при команде /start
def start_message(message):
    user = db.get_user(message)

    bot.send_message(message.chat.id, (
            'Привет, ' + message.from_user.first_name + '!'))  # Фтправка приветственного сообщения пользователю
    bot.send_message(message.chat.id, strings.initialization)

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)  # Фткрытие начального меню для работы с ботом
    menu_one = types.KeyboardButton(strings.start_message)
    markup.add(menu_one)
    bot.send_message(user["user_id"], strings.userFound)
    bot.send_message(user["user_id"], strings.greetings, reply_markup=markup)


@bot.message_handler(commands=['help'])  # Функция, вызываемая при команде /help
def get_help(message):
    bot.send_message(message.chat.id, strings.helpString)


@bot.message_handler(commands=['back'])  # Функция, возвращающая в главное меню
def go_back(message):
    open_main_menu(message)


@bot.message_handler(content_types=['text'])  # Функция ответчика на сообщения пользователя
def get_text_messages(message):
    content = message.text  # Текст сообщения пользователя

    if content == strings.start_message:
        open_main_menu(message)

    elif content == strings.regTraining:
        register.register_procedure(bot, message)  # Отлов кейса при выборе тренинга

    elif content == strings.backToMenu:
        open_main_menu(message)  # Отлов кейса при возврате в главное меню

    elif (content == strings.computerSafety) or (content == strings.webAndInternet) or (content == strings.passwordsAndLogins):
        request = register.create_new_request(message, content)

        if request == strings.request_decline:
            markup = types.InlineKeyboardMarkup(row_width=1)
            delete_entry = types.InlineKeyboardButton(strings.delete_entry, callback_data='delete' + content)
            markup.add(delete_entry)
            bot.send_message(message.chat.id, request)
            bot.send_message(message.chat.id, content, reply_markup=markup)
        else:
            bot.send_message(message.chat.id, request)

    elif content == strings.user_info:
        user_profile.open_user_info(bot, message)

    elif content == strings.show_requests:
        user_profile.get_requests(bot, message)

    elif content == strings.sertificate:
        certificates.get_certificate(bot, db.get_user(message))

    elif content == strings.show_info:
        user_profile.get_user_info(bot, message, db.get_user(message))

    elif content == strings.begin:
        bot.send_game(message.chat.id, game_short_name=config.GAMENAME)

    else:
        bot.send_message(message.chat.id,
                         strings.unsignedMessage)  # Отправка сообщения что бот не знает что ответить при недетерминированных кейсах


@bot.callback_query_handler(func=lambda callback_query: callback_query.game_short_name == config.GAMENAME)
def game(call):
    bot.answer_callback_query(callback_query_id=call.id, url=config.GAMEURL)


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    try:
        if call.message:
            if call.data == 'delete' + strings.passwordsAndLogins:
                register.delete_requests(call.message)
                bot.send_message(call.message.chat.id, strings.succsessfuly_delete)
            elif call.data == 'delete' + strings.computerSafety:
                register.delete_requests(call.message)
                bot.send_message(call.message.chat.id, strings.succsessfuly_delete)
            elif call.data == 'delete' + strings.webAndInternet:
                register.delete_requests(call.message)
                bot.send_message(call.message.chat.id, strings.succsessfuly_delete)
            elif call.data == 'back':
                open_main_menu(call.message)
    except Exception as e:
        print(repr(e))


# Функция для открытия главного меню бота
def open_main_menu(message):
    markup = types.ReplyKeyboardMarkup(row_width=1)
    menu_one = types.InlineKeyboardButton(strings.test, callback_data='primaryTest')
    menu_two = types.InlineKeyboardButton(strings.regTraining, callback_data='training')
    menu_three = types.InlineKeyboardButton(strings.begin, callback_data='startEducation')
    menu_four = types.InlineKeyboardButton(strings.user_info, callback_data='user_info')

    markup.add(menu_one, menu_two, menu_three, menu_four)

    bot.send_message(message.chat.id, strings.choice_item, reply_markup=markup) # Функция для открытия главного меню бота


bot.polling(none_stop=True, interval=0)
