from datetime import datetime
import os
from pathlib import Path

PATH_TO_FILE = Path(__file__).parent.parent / "data" / "operations.xlsx"


def get_time_for_greeting():
    """
    Функция принимает в формате YYYY-MM-DD HH:MM:SS и возвращает приветствие, например, 'Добрый день,
    в зависимости от времени суток
    """
    user_datetime = datetime.now()
    hour = user_datetime.hour
    if 5 <= hour < 12:
        return "Доброе утро"
    elif 12 <= hour < 18:
        return "Добрый день"
    elif 18 <= hour < 22:
        return "Добрый вечер"
    else:
        return "Добрый ночи"


def get_date_time(date_time: str, date_format: str = "%Y-%m-%d %H:%M:%S"):
    """
    Функция для страницы «Главная» принимает на вход строку с датой и временем в формате
    YYYY-MM-DD HH:MM:SS и возвращает период в виде списка строк
    """
    format_date = datetime.strptime(date_time, date_format).strftime("%d.%m.%Y %H:%M:%S")
    end_date = datetime.strptime(format_date, "%d.%m.%Y %H:%M:%S")
    year_end_date = end_date.year
    month_end_date = end_date.month
    hour_end_day = end_date.hour
    minute_end_day = end_date.minute
    second_end_day = end_date.second
    start_day = datetime(year_end_date, month_end_date, 1, hour_end_day, minute_end_day, second_end_day)
    start_day_str = datetime.strftime(start_day, "%d.%m.%Y %H:%M:%S")
    end_date_str = datetime.strftime(end_date, "%d.%m.%Y %H:%M:%S")
    period_date = [start_day_str, end_date_str]
    return period_date
