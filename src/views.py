from src.utils import get_time_for_greeting, get_date_time
import json
import os
from datetime import datetime
from typing import List, Any
import pandas as pd
from dotenv import load_dotenv

from src.utils import PATH_TO_FILE


def main(date):
    '''
    Функция для страницы «Главная» принимает на вход строку с датой и временем в формате
    YYYY-MM-DD HH:MM:SS и возвращающую JSON-ответ
    '''
    greeting = get_time_for_greeting()
    time_period: str = get_date_time(date)
    data = {
        "greeting": greeting,
        "time_period": time_period
    }
    json_data = json.dumps(data, ensure_ascii=False, indent=4)
    return json_data


def calculate_total_expenses(PATH_TO_FILE, card_number=None, category=None, cashback=False):
    """
    Считает общую сумму расходов из Excel-файла.
    """
    # Загружаем Excel-файл
    df = pd.read_excel(PATH_TO_FILE)

    # Фильтр: оставляем только завершённые операции ("OK") и отрицательные суммы (расходы)
    df_expenses = df[(df['Статус'] == 'OK') & (df['Сумма операции'] < 0)].copy()

    # Если указан номер карты, фильтруем по нему
    if card_number:
        df_expenses = df_expenses[df_expenses['Номер карты'] == card_number]
    if category:
        df_expenses = df_expenses[df_expenses['Категория'] == category]

    # Сумма расходов (без кэшбэка)
    total_expenses = df_expenses['Сумма операции'].abs().sum()

    # Если нужно учесть кэшбэк
    if cashback:
        total_cashback = df_expenses['Бонусы (включая кэшбэк)'].sum()
        net_expenses = total_expenses - total_cashback
        return round(net_expenses, 2)

