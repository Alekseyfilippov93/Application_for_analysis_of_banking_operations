from datetime import datetime
from pathlib import Path
import json
import os
from typing import List, Any, Dict, Union
import pandas as pd
from dotenv import load_dotenv
import yfinance as yf
import requests
from pandas import DataFrame

load_dotenv()

PATH_TO_FILE = Path(__file__).parent.parent / "data" / "operations.xlsx"

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
file_json = os.path.join(project_root, "user_settings.json")


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


def main(date):
    """
    Функция для страницы «Главная» принимает на вход строку с датой и временем в формате
    YYYY-MM-DD HH:MM:SS и возвращающую JSON-ответ
    """
    greeting = get_time_for_greeting()
    time_period: str = get_date_time(date)
    data = {"greeting": greeting, "time_period": time_period}
    json_data = json.dumps(data, ensure_ascii=False, indent=4)
    return json_data


def calculate_total_expenses(df, card_number=None, category=None, cashback=False):
    """
        Считает общую сумму расходов из Excel-файла.
    """
    # Фильтр: оставляем только завершённые операции ("OK") и отрицательные суммы (расходы)
    df_expenses = df[(df["Статус"] == "OK") & (df["Сумма операции"] < 0)].copy()

    # Если указан номер карты, фильтруем по нему
    if card_number:
        df_expenses = df_expenses[df_expenses["Номер карты"] == card_number]
    if category:
        df_expenses = df_expenses[df_expenses["Категория"] == category]

    # Сумма расходов (без кэшбэка)
    total_expenses = df_expenses["Сумма операции"].abs().sum()

    # Если нужно учесть кэшбэк
    if cashback:
        total_cashback = df_expenses["Бонусы (включая кэшбэк)"].sum()
        net_expenses = total_expenses - total_cashback
        result = round(net_expenses, 2)
        return result


def top_transactions_5(df: DataFrame) -> List[dict]:
    """Функция возвращает топ 5 транзакций"""
    sorted_df = df.sort_values("Сумма платежа", axis=0, ascending=False)
    result = [
        {
            "date": row['Дата платежа'],
            "category": row['Категория'],
            "amount": row['Сумма платежа'],
            "description": row['Описание'],
        }
        for _, row in sorted_df[:5].iterrows()
    ]
    print(result)
    return result


API_KEY = os.getenv("API_KEY")


def get_cur_rate(currencies: list) -> Dict[str, float]:
    """Функция для получения курса валют."""
    rates = {}
    for currency in currencies:
        url = f"https://api.apilayer.com/exchangerates_data/latest?symbols=RUB&base={currency}"
        response = requests.get(url, headers={"apikey": API_KEY}, timeout=40)
        rates[currency] = response.json()["rates"]["RUB"]
    return rates


if __name__ == "__main__":
    # Чтение user_settings.json и проверка отработки функции
    with open(file_json, "r", encoding="utf-8") as f:
        currencies = json.load(f)["user_currencies"]

    print(get_cur_rate(currencies))


def get_stock_prices() -> List[Dict[str, Union[str, float]]]:
    """
    Получает текущие цены акций из user_settings.json через Yahoo Finance.
    Возвращает список словарей вида {"stock": "AAPL", "price": 170.12}.
    """
    # Загружаем тикеры из файла
    with open(file_json, "r", encoding="utf-8") as f:
        symbols = json.load(f).get("user_stocks", [])  # Получаем список акций

    if not symbols:
        return []

    try:
        # Загружаем данные акций
        data = yf.download(
            tickers=" ".join(symbols),
            period="1d",
            group_by="ticker",
            progress=False
        )

        # Формируем результат
        return [
            {"stock": symbol, "price": round(float(data[symbol]["Close"][-1]), 2)}
            for symbol in symbols
            if symbol in data and not data[symbol]["Close"].empty
        ]
    except Exception as e:
        print(f"Ошибка при получении данных акций: {e}")
        return []


# Пример использования
if __name__ == "__main__":
    stocks = get_stock_prices()
    print(stocks)  # Вывод: [{"stock": "AAPL", "price": 170.12}, ...]


def convert_timestamps_to_strings(dataframe):
    """Преобразует все столбцы с типом 'datetime64[ns]' в строки."""
    for col in dataframe.select_dtypes(include=["datetime64[ns]"]).columns:
        dataframe[col] = dataframe[col].dt.strftime("%Y-%m-%d %H:%M:%S")
    return dataframe


def filter_date_operations(operations: pd.DataFrame, date: str) -> list:
    """Возвращает операции за текущий месяц"""
    first_day_moth = datetime.strptime(date, "%Y-%m-%d %H:%M:%S").replace(
        day=1, hour=00, minute=00, second=00
    )
    operations["Дата операции"] = pd.to_datetime(
        operations["Дата операции"], format="%d.%m.%Y %H:%M:%S"
    )
    return operations[
        (operations["Дата операции"] >= first_day_moth)
        & (operations["Дата операции"] <= datetime.strptime(date, "%Y-%m-%d %H:%M:%S"))
        ]
