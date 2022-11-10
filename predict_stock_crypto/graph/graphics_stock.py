# graph/graphics_stock.py
import datetime

import matplotlib.pyplot as plt
import pandas as pd

# Обновляем директорию для импорта модуля
from os import path
import sys

current = path.dirname(path.realpath(__file__))
parent = path.dirname(current)
sys.path.append(parent)
from config import settings

plt.style.use(settings.PYPLOT_SET_GRAPH)


def EMA_or_SMA(
    mov_avg: str, days_first: int, days_second: int, df: pd.DataFrame
) -> tuple:
    """
    Преимущество EMA в том, что в отличие от SMA, этот показатель реагирует
    быстрее на сигналы (но в тоже время может среагировать на ложный сигнал)
    ложные сигналы, а SMA хороша тем, что изменяет направление медленее,
    чем EMA, тем самым "гасит" ложные сигналы
    """
    df_days_first = pd.DataFrame()
    df_days_second = pd.DataFrame()
    match mov_avg:
        case "EMA":
            df_days_first["Close Price"] = (
                df["Close"].rolling(window=days_first).mean()
            )
            df_days_second["Close Price"] = (
                df["Close"].rolling(window=days_second).mean()
            )
            return df_days_first["Close Price"], df_days_second["Close Price"]
        case "SMA":
            df_days_first["Close Price"] = (
                df["Close"].ewm(span=days_first).mean()
            )
            df_days_second["Close Price"] = (
                df["Close"].ewm(span=days_second).mean()
            )
            return df_days_first["Close Price"], df_days_second["Close Price"]


def max_or_min(price_range: list, levels: str):
    """
    Высчитывает максимальную или минимальную цену в списке
    Аргумент:
        price_range(list): список цен
        levels(str): значение High или Low
    Возвращает:
        min \ max: максимальную или минимальную цену, либо 0 (ноль)
    """
    match levels:
        case "High":
            return max(price_range, default=0)
        case "Low":
            return min(price_range, default=0)

def levels(df: pd.DataFrame, levels: str):
    """
    Функция, которая на графике показывает макс. и мин. точки, после
    которых был разворот.
    """
    pivots = []
    dates = []
    counter = 0
    last_pivot = 0
    date_range = [zero * 0 for zero in range(1, 11)]
    match levels:
        case "High":
            price_range = [zero * 0 for zero in range(1, 11)]
        case "Low":
            price_range = [999999 for zero in range(1, 11)]
    for i in df.index:
        current_level = max_or_min(price_range=price_range, levels=levels)
        value = round(df[levels][i], 2)
        price_range = price_range[1:9]
        price_range.append(value)
        date_range = date_range[1:9]
        date_range.append(i)
        if current_level == max_or_min(price_range=price_range, levels=levels):
            counter += 1
        else:
            counter = 0
        match counter:
            case 5:
                last_pivot = current_level
                dateloc = price_range.index(last_pivot)
                last_date = date_range[dateloc]
                pivots.append(last_pivot)
                dates.append(last_date)
    return dates, pivots


def stock_to_graph(
    df: pd.DataFrame,
    from_date: str,
    today_date: str,
    stock: str,
    function: str,
    days_first: int = 30,
    days_second: int = 60,
) -> str:
    """
    В зависимости от переданной строки в "function", выполняет:
     - EMA | SMA = рассчитывает скользящую среднюю;
     - High | Low = рисует точки, на которых был разворот по цене.
     - days_first | days_second = диапозоны сдвига для скользящих средних
        (по-умолчанию, 30 дней | 60 дней)
    """
    data_to_graph = pd.DataFrame()
    data_to_graph["Stock"] = df["Close"]
    # Визуализируем
    plt.figure(figsize=(15, 6.5))
    plt.title(str(stock) + " график " + function)
    plt.xlabel(from_date + " - " + today_date)
    plt.ylabel("Цена")
    try:
        match function:
            case "EMA" | "SMA":
                label_first = function + (str(days_first))
                label_second = function + (str(days_second))
                (
                    data_to_graph[label_first],
                    data_to_graph[label_second],
                ) = EMA_or_SMA(
                    moving_average=function,
                    days_first=days_first,
                    days_second=days_second,
                    df=df,
                )
                plt.plot(
                    data_to_graph["Stock"], label=stock, alpha=1, linewidth=3
                )
                plt.plot(
                    data_to_graph[label_first], label=label_first, alpha=0.85
                )
                plt.plot(
                    data_to_graph[label_second], label=label_second, alpha=0.85
                )
            case "High" | "Low":
                time_delta = datetime.timedelta(days=15)
                dates, pivots = levels(df=df, levels=function)
                plt.plot(df[function], label=stock, alpha=0.35, linewidth=3)
                for index in range(len(pivots)):
                    plt.plot_date(
                        [dates[index], dates[index] + time_delta],
                        [pivots[index], pivots[index]],
                        linewidth=3,
                        fmt="-",
                        alpha=1,
                    )
    except Exception as error:
        settings.logging.error(f"Ошибка ({error}) при построении графиков")
    plt.legend(loc="best")
    name_pic = function + ".png"
    current_img = path.join(settings.IMG_DIR, name_pic)
    plt.savefig(current_img, bbox_inches="tight")
    return name_pic
