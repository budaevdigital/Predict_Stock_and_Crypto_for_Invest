# parse/parse.py
# Обновляем директорию для импорта встроенных модулей
from os import path
from sys import path as sys_path

current = path.dirname(path.realpath(__file__))
parent = path.dirname(current)
sys_path.append(parent)
import investpy
import pandas as pd
import requests
from config import settings


def get_all_cryptos() -> dict[str, str]:
    """
    Получает список доступных криптовалют в виде ассоциативного
    массива (словаря)
    """
    # Уточняем нужные "столбцы". По-умолчанию доступно также 'currency'
    return investpy.crypto.get_cryptos_dict(columns=["name", "symbol"])


def get_historical_data(
    symbol: str, from_date: str, today_date: str, is_crypto: bool, country: str
) -> pd.DataFrame:
    """
    Функция использует библиотеку investpy и возвращает DataFrame
    подобного содержания:
    ---------------------------------------------------------------------
    Date        Open     High     Low      Close    Volume       Currency
    2021-06-01  2707.94  2738.23  2529.73  2633.67  2451500      USD
    """
    match is_crypto:
        case True:
            try:
                return investpy.get_crypto_historical_data(
                    crypto=symbol, from_date=from_date, to_date=today_date
                )
            except Exception as error:
                settings.logging.exception(
                    f"Ошибка ({error}) при запросе исторических "
                    "данных с investpy",
                    stack_info=True,
                )
                return None
        case False:
            try:
                return investpy.get_stock_historical_data(
                    stock=symbol,
                    country=country,
                    from_date=from_date,
                    to_date=today_date,
                )
            except Exception as error:
                settings.logging.exception(
                    f"Ошибка ({error}) при запросе исторических "
                    "данных с investpy",
                    stack_info=True,
                )
                return None


def get_price_from_binance(symbol: str) -> str:
    """
    Делает запрос в api binance, чтобы узнать точную цену криптовалюты
    Аргумент:
        symbol(str): символ криптовалюты (НЕ ИМЯ)
    Возвращает:
        str: цена криптовалюты. До 2 знаков после запятой
    Исключения:
        ConnectionError: в случае, если сайт будет недоступен
    """
    symbol = symbol.upper()
    try:
        response = requests.get(
            f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}USDT"
        ).json()
    except Exception as error:
        settings.logging.exception(
            f"Ошибка ({error}) при парсинге цен на binance", stack_info=True
        )
    return format(float(response["price"]), ".2f")
