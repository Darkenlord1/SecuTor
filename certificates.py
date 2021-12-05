# Импорт необходимых библиотек
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import datetime
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
            if not user["certificate_received"]:
                certificate = {
                    "user_id": user["user_id"],
                    "first_name": user["first_name"],
                    "last_name": user["last_name"],
                    "received_date": 0
                }

                self.certificates.insert_one(certificate)
                return certificate
        else:
            result = strings.course_not_passed
            return result

    def set_date(self, user, date):
        self.certificates.update_one({"user_id": user["user_id"]}, {'$set': {"received_date": date}})


certificates = Certificate()


def get_certificate(bot, user):
    result = certificates.get_certificate(user)

    if result != strings.course_not_passed:
        if not user["certificate_received"]:
            bot.send_message(user["user_id"], strings.course_passed)
            image = generate_doc(user)
            image.save('received_certificate.jpg')
            bot.send_photo(user["user_id"], photo=open('received_certificate.jpg', 'rb'))
        else:
            bot.send_message(user["user_id"], strings.certificate_received)
    else:
        bot.send_message(user["user_id"], result)


def generate_doc(user):
    img = Image.open('certificate.jpg')

    font = ImageFont.truetype("arial.ttf", size=50)
    description_font = ImageFont.truetype("arial.ttf", size=30)
    date_font = ImageFont.truetype("arial.ttf", size=30)

    now = datetime.datetime.now()
    date = str(now.day) + '.' + str(now.month) + '.' + str(now.year)
    first_name = user["first_name"]
    last_name = user["last_name"]
    receiver = first_name + ' ' + last_name

    font_color = (0, 0, 0, 0)
    name_pos = (300, 300)
    date_pos = (175, 500)
    description_pos = (250, 380)
    entry_pos = (350, 220)

    drawing = ImageDraw.Draw(img)
    drawing.text(name_pos, receiver, font=font, fill=font_color)
    drawing.text(date_pos, date, font=date_font, fill=font_color)
    drawing.text(description_pos, strings.certificate_description, font=description_font, fill=font_color)
    drawing.text(entry_pos, strings.certificate_entry, font=font, fill=font_color)

    certificates.set_date(user, date)

    return img
