# tests/test_parse.py

import unittest
from os import path
from sys import path as sys_path

import pandas as pd

# Обновляем директорию для импорта встроенных модулей
current = path.dirname(path.realpath(__file__))
parent = path.dirname(current)
sys_path.append(parent)

from parse import parse
from parse import predict_parse


class TestParse(unittest.TestCase):
    """
    Тестирует работу парсеров, используемых в боте
    """

    def test_lists_all_cryptos(self):
        """Получение всего списка криптовалюты. Investpy"""
        task = parse.get_all_cryptos()
        self.assertIsInstance(task, list, "Был получен не список")

    def test_get_historical_data(self):
        """Получение исторических данных"""
        crypto_btc = {
            "Date": "2020-04-01",
            "Open": "6412.4",
            "High": "6661.3",
            "Low": "6157.4",
            "Close": "6638.5",
            "Volume": "1398824",
            "Currency": "USD",
        }
        task = parse.get_historical_data(
            symbol="bitcoin",
            from_date="01/04/2020",
            today_date="02/04/2020",
            is_crypto=True,
            country="United States",
        )
        self.assertIsInstance(
            task, pd.DataFrame, "Был получен формат отличный от DataFrame"
        )
        for key, value in task.items():
            self.assertEqual(
                crypto_btc[key], str(value[0]), "Неверные исторические данные"
            )

    def test_get_price_from_binance(self):
        """
        Тест запроса точной цены на криптовалюту в Binance
        """
        task = parse.get_price_from_binance("btc")
        self.assertIsInstance(task, str, "Возвращён неверный формат")


class TestPredictParse(unittest.TestCase):
    """
    Тестирует работу парсинга предсказываемой цены криптовалюты
    """
    def test_get_html_from_url_response(self):
        url = 'https://yandex.ru'
        task = predict_parse.get_html_from_url_response(url)
        self.assertEqual(task.status_code, 200, "Проблема со связью")

    def test_get_predict_price_1_to_14_days(self):
        name_cryptos = 'bitcoin'
        task = predict_parse.get_predict_price_1_to_14_days(name_cryptos)
        self.assertIsInstance(task, str, "При парсинге предсказания с "
                              "walletinvestor, что-то пошло не так")


if __name__ == "__main__":
    unittest.main()
