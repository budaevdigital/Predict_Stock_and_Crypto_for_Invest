# parse/predict_parse.py

from datetime import date, timedelta
from bs4 import BeautifulSoup
import requests
# Обновляем директорию для импорта встроенных модулей
from os import path
from sys import path as sys_path


current = path.dirname(path.realpath(__file__))
parent = path.dirname(current)
sys_path.append(parent)

from config import settings
from parse.user_agents_for_parse import (
    get_random_header_user_agent as head_user_agent,
)


def get_html_from_url_response(url: str):
    """
    Делает запрос с подстановкой рандомного header-user-agent
    Аргумент:
        url(str): ссылка
    Возвращает:
        Response: ответ сервера
    Исключения:
        ConnectionError: в случае, если сайт будет недоступен
    """
    header = head_user_agent()
    response = requests.get(url=url, headers=header)
    if response.status_code != 200:
        settings.logging.error(
            f"Ошибка в ({response}) - Проблема с доступностью сайта"
        )
        raise ConnectionError(
            f"Проблемы с соединением: код ответа {response.status_code}!"
        )
    return response


def get_predict_price_1_to_14_days(name_crypto: str) -> str:
    """
    Парсит прогнозируемую цену крипты на ближайшие две недели и
    возвразает ассоциативный массив (словарь)
    Аргументы:
        name_crypto(str): принимает строку, имя криптовалюты (не символ)
    Возвращает:
        str: сформированную строку с датой и ценой
    Исключения:
        ValueError: в случае, если цена в парсинге оказалась пустой
    """
    all_predict_dict = ""
    name_crypto = name_crypto.lower()
    url = f"https://walletinvestor.com/forecast/{name_crypto}-prediction"
    response = get_html_from_url_response(url)
    dirty_parse_response = BeautifulSoup(response.text, "lxml")
    for count in range(0, 14):
        predict_price = (
            dirty_parse_response.find(attrs={"data-key": str(count)})
            .findNext(attrs={"data-col-seq": "1"})
            .text[7:]
            .strip()
        )
        if predict_price is None:
            settings.logging.error(
                f"Ошибка в ({predict_price}) при парсинге предсказания "
                "с сайта walletinvestor"
            )
            raise ValueError(
                "Проблема с парсингом. Значение цены не может быть пустым"
            )
        # к дате прибавим 1, т.к. отчёт с 0
        date_predict = str(
            date.today() + timedelta(days=1) + timedelta(days=count)
        )
        all_predict_dict += (
            str(date_predict)
            + " | "
            + str(format(float(predict_price), ".2f"))
            + " $ \n"
        )
    return all_predict_dict
