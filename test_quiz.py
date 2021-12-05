# Импорт необходимых библиотек
import telebot
from telebot import types
import strings
import config
from pymongo import MongoClient


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


bot = telebot.TeleBot(config.TESTTOKEN)
testing = Testing()


def start(message):
    user = testing.get_user(message.chat.id)

    if user["is_passed"]:
        bot.send_message(message.from_user.id, 'увы(')
        return

    if user["is_passing"]:
        return

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

    user["question_index"] += 1
    testing.set_user((query.message.chat.id, {"question_index": user["question_index"]}))

    post = get_question_message(user)
    if post:
        bot.edit_message_text(post["text"], query.message.chat.id, query.message.id, reply_markup=post["keyboard"])


def get_question_message(user):
    if user["question_index"] == testing.question_count:
        count = 0
        for question_index, question in enumerate(testing.questions.find({})):
            if question["correct"] == user["answers"][question_index]:
                count += 1

            percents = round(100 * count / testing.question_count)

            text = 'вы ответили правильно...'

            testing.set_user(user["chat_id"], {"is_passed": True, "is_passing": False})

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
            text += " галочка"
        elif answer_index == user["answers"][-1]:
            text += " nonono"

        text += "\n"

    keyboard = types.InlineKeyboardMarkup()
    keyboard.row(types.InlineKeyboardButton("Далее", callback_data="?next"))

    return {
        "text": text,
        "keyboard": keyboard
    }
