from os import path
import sys
# Обновляем директорию для импорта модуля
current = path.dirname(path.realpath(__file__))
parent = path.dirname(current)
sys.path.append(parent)

import telegram
from config import settings

bot = telegram.Bot(token=settings.TOKEN)

def send_message(message: str):
    """
    Принимаем и пересылаем текстовое сообщение
    (CHATID задаётся в settings.py)
    """
    bot.send_message(settings.CHAT_ID, message)

def send_photo(name_img: str):
    """
    Принимаем название графика (в IMG) и пересылаем его
    (CHATID задаётся в settings.py)
    """
    current_img = path.join(settings.IMG_DIR, name_img)
    with open (current_img, 'rb') as img:
        bot.send_photo(settings.CHAT_ID, img)
