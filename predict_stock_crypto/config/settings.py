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








# БЛОК ПОЛЬЗОВАТЕЛЬСКИХ НАСТРОЕК
# Основной блок программы
counter_stock = 0


# для подсчёта кол-ва обработанных акций
counter_index = 0
index = 1
good_stocks = []
error_stock = []

# выбрать интервал - 5mins, 15mins, 30mins, 1hour, 5hours, daily, weekly and monthly
interval_index = '1hour'

# время интервала для сна (в cекундах)
time_sleep = 3

# выводить данные в консоль? (True = да \ False = нет)
text_in_console = False

# отсылать сообщения в телеграм ?
telegram_on_off = True

# отсылать графики в телеграм ?
telegram_on_graph = True

# отсылать сообщения об ошибке в телеграм ?
telegram_error_on = False

# загрузить список акций с csv файла, или проверить весь перечень с сайта?
stock_in_net = False  # False - грузит таблицу с акциями Тиньков Инвестиции

# Перемешать список акций?
random_stocks_on = True

# Задаём условия для проверки акций
# tech_buy < x1 or tech_sell > x2 or moving_sma_buy < x3 or moving_ema_buy < x4 or last_price_df > x5
# [x1, x2, x3, x4, x5]
# x1 - количество сигналов на покупку (макс. 12). По умолчанию 10.
# х2 - количество сигналов на продажу (макс. 12). По умолчанию 2.
# х3 - количество сигналов на покупку по SMA по выбранному интервалу (5mins, 15mins, 30mins, 1hour, 5hours, daily, weekly and monthly). По умолчанию 4
# х4 - количество сигналов на покупку по EMA по выбранному интервалу (5mins, 15mins, 30mins, 1hour, 5hours, daily, weekly and monthly). По умолчанию 4
# x5 - максимальная цена акций, дороже которой акции не рассматривать. По-умолчанию 100$
checking_stock = [8, 3, 4, 4, 100]

