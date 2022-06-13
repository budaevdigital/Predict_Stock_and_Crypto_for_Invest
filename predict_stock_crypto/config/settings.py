#config/settings.py

import logging
from logging.handlers import RotatingFileHandler  
import os
from pathlib import Path
from dotenv import load_dotenv

# Загрузим переменные окружения
load_dotenv()

# Выбираем абсолютный путь - берём за основу этот файл и поднимаемся на две директории выше
BASE_DIR = Path(__file__).resolve().parent.parent
IMG_DIR = os.path.join(BASE_DIR, 'img')
STOCKS_CRYPTO_DIR = os.path.join(BASE_DIR, 'stocks_list')
DATABASE_DIR = os.path.join(BASE_DIR, 'database')
DATABASE = os.path.join(DATABASE_DIR, 'users.db')
CONFIG_DIR = os.path.join(BASE_DIR, 'config')
LOGGING_DIR = os.path.join(CONFIG_DIR, 'logging')
LOGGING = os.path.join(LOGGING_DIR, 'logfile.log')

# Количество избранных валют у каждого пользователя
WATCHLIST_POSITION = 3

COUNTRY = 'United States'

# специальное отображение графиков для pyplot fivethirtyeight
PYPLOT_SET_GRAPH = 'fivethirtyeight'

# При работе с переменными окружения, будем использовать getenv
# В отличии от environ, getenv не вызывает исключения,
# а возвращает None
TOKEN = os.getenv('TOKEN')
CHAT_ID = int(os.getenv('CHATID'))

# Здесь задана глобальная конфигурация для всех логгеров 
logging.basicConfig(
        handlers=[RotatingFileHandler(LOGGING, maxBytes=100000, backupCount=5)],
        level=logging.ERROR,
        format="[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s",
        datefmt='%Y-%m-%d | T%H:%M:%S')
