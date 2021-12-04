#Импорт необходимых библиотек
import telebot
from telebot import types
import config
import strings
import register
import pandas

#Токен для бота, чтобы он мог общаться в телеграме
bot = telebot.TeleBot(config.TOKEN)

#Эвент отлова сообщения, вывод приветственного сообщения при запуске бота
@bot.message_handler(commands=['start'])
def start_message(message):
    with open(config.DBFILE, 'w', newline='') as db:
        user = message.from_user.id
        db = pandas.read_csv(config.DBFILE)


        if not db.userID.loc[db.userID == user]:
            
            

    markup = types.ReplyKeyboardMarkup(row_width=2)

    #Три кнопки для выбора дальнейших действий
    menu1 = types.InlineKeyboardButton(strings.test, callback_data='primaryTest')
    menu2 = types.InlineKeyboardButton(strings.regTraining, callback_data='training')
    menu3 = types.InlineKeyboardButton(strings.begin, callback_data='startEducation')

    markup.add(menu1, menu2, menu3) #Само меню выбора

    #Отправка приветственного сообщения
    bot.send_message(message.chat.id, strings.greetings, reply_markup=markup)

#Эвент отлова сообщения помощи
@bot.message_handler(commands=['help'])
def get_help(message):
    bot.send_message(message.chat.id, strings.helpString)

#Эвент отлова ответов пользователя
@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    content = message.text
    #print(content, strings.regTraining)

    if content == strings.regTraining:
        register.registerProcedure(bot, message) #Отлов кейса при выборе тренинга
    elif content == strings.backToMenu:
        start_message(message) #Отлов кейса при возврате в главное меню
    else:
        bot.send_message(message.chat.id, strings.unsignedMessage) #Отправка сообщения что бот не знает что ответить при недетерминированных кейсах


bot.polling(none_stop=True, interval=0)