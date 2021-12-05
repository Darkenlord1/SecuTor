# Импорт необходимых библиотек
from PIL import Image
from PIL import ImageDraw
import telebot
from telebot import types
import strings
import config
from pymongo import MongoClient


class Certificate:
    def __init__(self):
        cluster = MongoClient(config.DBURL)  # Подклчение к Mongo-клиенту

        self.db = cluster["SecuTor"]  # Инициация кластера из MongoBD
        self.certificates = self.db["Certificates"]  # Инициация коллекции из MongoBD

    def get_certificate(self, user):
        if user["course_passed"]:
            print('something is happening...')

            certificate = {
                "user_id": user["user_id"],
                "first_name": user["first_name"],
                "last_name": user["last_name"]
            }

            self.certificates.insert_one(certificate)
            return certificate

        else:
            result = strings.course_not_passed
            return result


certificates = Certificate()


def get_certificate(bot, user):
    result = certificates.get_certificate(user)

    if result != strings.course_not_passed:
        image = generate_doc(user)
        image.save('test.jpg')
        bot.send_photo(user["user_id"], photo=open('test.jpg', 'rb'))
    else:
        bot.send_message(user["user_id"], result)


def generate_doc(user):
    img = Image.open('1.jpg')

    font_color = (74, 75, 69)  # Цвет шрифта
    first_name_pos = (585, 172)  # Координаты первой буквы фамилии на картинке 1.jpg
    second_name_pos = (505, 205)  # Координаты первой буквы имени

    drawing = ImageDraw.Draw(img)
    drawing.text(first_name_pos, user["first_name"], font=font, fill=font_color)
    drawing.text(second_name_pos, user["last_name"], font=font, fill=font_color)

    return img
