
from datetime import date, timedelta
from bs4 import BeautifulSoup
import requests
from user_agents_for_parse import (get_random_header_user_agent 
                                    as head_user_agent)

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
        raise ConnectionError (f'Проблемы с соединением: код ответа {response.status_code}!')
    return response

def get_predict_price_1_to_14_days(name_crypto: str) -> dict[str, float]:
    """
    Парсит прогнозируемую цену крипты на ближайшие две недели и возвразает ассоциативный массив (словарь)
    Аргументы:
        name_crypto(str): принимает строку, имя криптовалюты (не символ)
    Возвращает:
        dict[str, float]: словарь {'дата' : 'цена'}
    Исключения:
        ValueError: в случае, если цена в парсинге оказалась пустой
    """
    all_predict_dict = {}
    name_crypto = name_crypto.lower()
    url = f'https://walletinvestor.com/forecast/{name_crypto}-prediction'
    response = get_html_from_url_response(url)
    dirty_parse_response = BeautifulSoup(response.text, 'lxml')
    for count in range(0, 14):
        predict_price = dirty_parse_response.find(attrs={'data-key': str(count)}).findNext(attrs={'data-col-seq': '1'}).text[7:].strip()
        if predict_price is None:
            raise ValueError ('Проблема с парсингом. Значение цены не может быть пустым')
        # к дате прибавим 1, т.к. отчёт с 0
        date_predict = str(date.today() + timedelta(days=1) + timedelta(days=count))
        all_predict_dict[str(date_predict)] = format(float(predict_price), '.2f')
    return all_predict_dict
