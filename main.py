# Импорт необходимых библиотек
import telebot
from pymongo import MongoClient
from telebot import types
import config
import strings
import register
import user_profile
import certificates
import test_quiz

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
                "course_passed": False,
                "certificate_received": False
            }

            self.users.insert_one(user)

            return user

    def update(self, message):
        self.users.update_one({"user_id": message.from_user.id}, {'$set': {"certificate_received": True}})


class Testing:
    def __init__(self):
        cluster = MongoClient(config.DBURL)  # Подклчение к Mongo-клиенту

        self.db = cluster["SecuTor"]  # Инициация кластера из MongoBD
        self.users = self.db["Questions_users"]  # Инициация коллекции из MongoBD
        self.questions = self.db["Questions"]  # Инициация коллекции из MongoBD

        self.question_count = len(list(self.questions.find({})))

    def get_user(self, user_id):
        user = self.users.find_one({"user_id": user_id})

        if user:
            return user

        else:
            user = {
                "user_id": user_id,
                "is_passed": False,
                "is_passing": False,
                "question_index": None,
                "answers": []
            }

            self.users.insert_one(user)

            return user

    def set_user(self, user_id, update):
        self.users.update_one({"user_id": user_id}, {'$set': update})

    def get_question(self, index):
        return self.questions.find_one({"id": index})


db = DataBase()  # Инициация объекта базы данных
testing = Testing()


@bot.message_handler(commands=['test'])
def start(message):
    user = testing.get_user(message.chat.id)

    if user["is_passed"]:
        bot.send_message(message.from_user.id, 'увы(')
        return

    #if user["is_passing"]:
        #return

    testing.set_user(message.chat.id, {"question_index": 0, "is_passing": True})

    user = testing.get_user(message.chat.id)
    post = get_question_message(user)
    if post:
        bot.send_message(message.from_user.id, post["text"], reply_markup=post["keyboard"])


@bot.callback_query_handler(func=lambda query: query.data.startswith("?ans"))
def answered(query):
    user = testing.get_user(query.message.chat.id)

    if user is None or user["is_passed"] or not user["is_passing"]:
        return

    user["answers"].append(int(query.data.split("&")[1]))
    testing.set_user(query.message.chat.id, {"answers": user["answers"]})

    post = get_answered_message(user)
    if post:
        bot.edit_message_text(post["text"], query.message.chat.id, query.message.id, reply_markup=post["keyboard"])


@bot.callback_query_handler(func=lambda query: query.data == "?next")
def next_question(query):
    user = testing.get_user(query.message.chat.id)

    if user["is_passed"] or not user["is_passing"]:
        return
    print(user["question_index"])
    user["question_index"] += 1
    print(user["question_index"])
    testing.set_user(query.message.chat.id, {"question_index": user["question_index"]})

    post = get_question_message(user)
    if post:
        bot.edit_message_text(post["text"], query.message.chat.id, query.message.id, reply_markup=post["keyboard"])


def get_question_message(user):
    print("hello world")
    if user["question_index"] == testing.question_count:
        print(5)
        count = 0
        for question_index, question in enumerate(testing.questions.find({})):
            if question["correct"] == user["answers"][question_index]:
                count += 1

            percents = round(100 * count / testing.question_count)

            text = 'вы ответили правильно...'

            testing.set_user(user["user_id"], {"is_passed": True, "is_passing": False})

            return {
                "text": text,
                "keyboard": None
            }

    question = testing.get_question(user["question_index"])

    if question is None:
        return

    keyboard = types.InlineKeyboardMarkup()
    for answer_index, answer in enumerate(question["answers"]):
        keyboard.row(types.InlineKeyboardButton(f"{chr(answer_index + 97)}) {answer}",
                                                callback_data=f"?ans&{answer_index}"))

    text = f"Вопрос №{user['question_index'] + 1}\n\n{question['text']}"

    return {
        "text": text,
        "keyboard": keyboard
    }


def get_answered_message(user):
    question = testing.get_question(user["question_index"])

    text = f"Вопрос №{user['question_index'] + 1}\n\n {question['text']}\n"

    for answer_index, answer in enumerate(question["answers"]):
        text += f"{chr(answer_index + 1)} {answer}"

        if answer_index == question["correct"]:
            text += " ✅"
        elif answer_index == user["answers"][-1]:
            text += " ❌"

        text += "\n"

    keyboard = types.InlineKeyboardMarkup()
    keyboard.row(types.InlineKeyboardButton("Далее", callback_data="?next"))

    return {
        "text": text,
        "keyboard": keyboard
    }


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

    elif (content == strings.computerSafety) or (content == strings.webAndInternet) or (
            content == strings.passwordsAndLogins):
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

    elif content == strings.test:
        start(message)

    elif content == strings.sertificate:
        certificates.get_certificate(bot, db.get_user(message))
        db.update(message)

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

    bot.send_message(message.chat.id, strings.choice_item,
                     reply_markup=markup)  # Функция для открытия главного меню бота


bot.polling(none_stop=True, interval=0)
