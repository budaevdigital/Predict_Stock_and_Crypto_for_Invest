import os
from pathlib import Path
from csv import reader
from dotenv import load_dotenv
from . import client_settings

# Загрузим переменные окружения
load_dotenv()

# TODO - настироить в дальнейшем систему логирования
DEBUG = True

# Выбираем абсолютный путь - берём за основу этот файл и поднимаемся на две директории выше
BASE_DIR = Path(__file__).resolve().parent.parent
IMG_DIR = os.path.join(BASE_DIR, 'img')
STOCKS_CRYPTO_DIR = os.path.join(BASE_DIR, 'stocks_list')
DATABASE_DIR = os.path.join(BASE_DIR, 'database')
DATABASE = os.path.join(DATABASE_DIR, 'users.db')


# При работе с переменными окружения, будем использовать getenv
# В отличии от environ, getenv не вызывает исключения,
# а возвращает None
TOKEN = os.getenv('TOKEN')
CHAT_ID = int(os.getenv('CHATID'))

try:
    match client_settings.is_crypto_parse:
        case True:
            # Читаем csv файл со списком крипты
            with open(os.path.join(STOCKS_CRYPTO_DIR, 'crypto.csv'), newline='') as Cryptos:
                data_cryptos = reader(Cryptos)
                SYMBOL_DATA_LIST = [row for row in data_cryptos]
        case False:
            # Читаем csv файл со списком акций
            with open(os.path.join(STOCKS_CRYPTO_DIR, 'stock.csv'), newline='') as Stocks:
                data_stocks = reader(Stocks)
                SYMBOL_DATA_LIST = [row for row in data_stocks]
except Exception as error:
    # TODO - в логах задать, что возникла проблема с чтением файла
    print(error)
