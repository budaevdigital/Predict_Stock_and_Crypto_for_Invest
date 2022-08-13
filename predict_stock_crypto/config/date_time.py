# config/date_time.py
from typing import Union
from datetime import date


def set_current_to_from_date() -> Union[dict[str, str], None]:
    """
    Функция, которая вернёт ассоциативный массив(словарь) с двумя датами:
     - dict['today'] = Сегодняшнюю;
     - dict['old-date'] = Год назад
    """
    dict_date = {}
    dict_date["today"] = (
        str(date.today().day)
        + "/"
        + str(date.today().month)
        + "/"
        + str(date.today().year)
    )
    day_month = date.today().month
    # Конструкция match-case работает начиная с Python3.10
    match day_month:
        # Условие - если месяц январь или февраль (это начало года),
        # то берём дату двухгодичную
        case 1 | 2:
            dict_date["old-date"] = (
                str(1) + "/" + str(12) + "/" + str(date.today().year - 2)
            )
            return dict_date
        case _:
            dict_date["old-date"] = (
                str(1)
                + "/"
                + str(date.today().month)
                + "/"
                + str(date.today().year - 1)
            )
            return dict_date
