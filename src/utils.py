import logging
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

# Настройка логирования
logging.basicConfig(
    filename='app.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()

PATH_TO_FILE = Path(__file__).parent.parent / "data" / "operations.xlsx"

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
file_json = os.path.join(project_root, "user_settings.json")


def get_time_for_greeting():
    """
    Функция принимает в формате YYYY-MM-DD HH:MM:SS и возвращает приветствие, например, 'Добрый день,
    в зависимости от времени суток
    """
    try:
        user_datetime = datetime.now()
        hour = user_datetime.hour
        greeting = "Добрый ночи"  # значение по умолчанию

        if 5 <= hour < 12:
            greeting = "Доброе утро"
        elif 12 <= hour < 18:
            greeting = "Добрый день"
        elif 18 <= hour < 22:
            greeting = "Добрый вечер"

        logger.debug(f"Определено приветствие: {greeting}")
        return greeting
    except Exception as e:
        logger.error(f"Ошибка при определении приветствия: {str(e)}")
        return "Добрый день"  # значение по умолчанию при ошибке


def get_date_time(date_time: str, date_format: str = "%Y-%m-%d %H:%M:%S"):
    """
    Функция для страницы «Главная» принимает на вход строку с датой и временем в формате
    YYYY-MM-DD HH:MM:SS и возвращает период в виде списка строк
    """
    try:
        logger.debug(f"Обработка даты: {date_time}")
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
        logger.debug(f"Период: {period_date}")
        return period_date
    except Exception as e:
        logger.error(f"Ошибка при обработке даты: {str(e)}")
        return []


def main(date):
    """
    Функция для страницы «Главная» принимает на вход строку с датой и временем в формате
    YYYY-MM-DD HH:MM:SS и возвращающую JSON-ответ
    """
    try:
        logger.info("Запуск функции main")
        greeting = get_time_for_greeting()
        time_period = get_date_time(date)
        data = {"greeting": greeting, "time_period": time_period}
        json_data = json.dumps(data, ensure_ascii=False, indent=4)
        logger.info(f"Сформирован JSON: {json_data}")
        return json_data
    except Exception as e:
        logger.error(f"Ошибка в main: {str(e)}")
        return {}


def calculate_total_expenses(df, card_number=None, category=None, cashback=False):
    """
        Считает общую сумму расходов из Excel-файла.
    """
    try:
        logger.info(f"Начало расчета расходов. Параметры: card_number={card_number}, "
                    f"category={category}, cashback={cashback}")

        # Фильтр: оставляем только завершённые операции ("OK") и отрицательные суммы (расходы)
        df_expenses = df[(df["Статус"] == "OK") & (df["Сумма операции"] < 0)].copy()
        logger.debug(f"Найдено {len(df_expenses)} операций расходов после базовой фильтрации")

        # Если указан номер карты, фильтруем по нему
        if card_number:
            df_expenses = df_expenses[df_expenses["Номер карты"] == card_number]
            logger.debug(f"После фильтрации по карте {card_number} осталось {len(df_expenses)} операций")

        if category:
            df_expenses = df_expenses[df_expenses["Категория"] == category]
            logger.debug(f"После фильтрации по категории '{category}' осталось {len(df_expenses)} операций")

        # Сумма расходов (без кэшбэка)
        total_expenses = df_expenses["Сумма операции"].abs().sum()
        logger.info(f"Общая сумма расходов (без кэшбэка): {total_expenses:.2f}")

        # Если нужно учесть кэшбэк
        if cashback:
            total_cashback = df_expenses["Бонусы (включая кэшбэк)"].sum()
            net_expenses = total_expenses - total_cashback
            result = round(net_expenses, 2)
            logger.info(f"Учет кэшбэка. Сумма кэшбэка: {total_cashback:.2f}, "
                        f"Итоговая сумма с учетом кэшбэка: {result:.2f}")
            return result

        logger.info(f"Возвращаемая сумма расходов: {round(total_expenses, 2):.2f}")
        return round(total_expenses, 2)

    except Exception as e:
        logger.error(f"Ошибка при расчете расходов: {str(e)}", exc_info=True)
        raise


def top_transactions_5(df: DataFrame) -> List[dict]:
    """Функция возвращает топ 5 транзакций"""
    try:
        logger.info("Начало выполнения top_transactions_5")
        logger.debug(f"Размер входного DataFrame: {df.shape}")

        sorted_df = df.sort_values("Сумма платежа", axis=0, ascending=False)
        logger.debug("Данные успешно отсортированы по сумме платежа")

        result = [
            {
                "date": row['Дата платежа'],
                "category": row['Категория'],
                "amount": row['Сумма платежа'],
                "description": row['Описание'],
            }
            for _, row in sorted_df[:5].iterrows()
        ]

        logger.info(f"Топ-5 транзакций успешно сформирован: {result}")
        return result

    except Exception as e:
        logger.error(f"Ошибка в top_transactions_5: {str(e)}", exc_info=True)
        raise


API_KEY = os.getenv("API_KEY")


def get_cur_rate(currencies: list) -> Dict[str, float]:
    """Функция для получения курса валют."""
    try:
        logger.info(f"Начало получения курсов валют для: {currencies}")
        rates = {}

        for currency in currencies:
            url = f"https://api.apilayer.com/exchangerates_data/latest?symbols=RUB&base={currency}"
            logger.debug(f"Запрос курса для валюты {currency}")

            response = requests.get(url, headers={"apikey": API_KEY}, timeout=40)
            response.raise_for_status()

            rate = response.json()["rates"]["RUB"]
            rates[currency] = rate
            logger.debug(f"Получен курс {currency}->RUB: {rate}")

        logger.info(f"Успешно получены курсы валют: {rates}")
        return rates

    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка при запросе курса валют: {str(e)}", exc_info=True)
        raise
    except Exception as e:
        logger.error(f"Неожиданная ошибка в get_cur_rate: {str(e)}", exc_info=True)
        raise


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
    try:
        logger.info("Начало получения цен акций")

        # Загружаем тикеры из файла
        with open(file_json, "r", encoding="utf-8") as f:
            symbols = json.load(f).get("user_stocks", [])

        logger.debug(f"Получены тикеры акций: {symbols}")

        if not symbols:
            logger.info("Список акций пуст, возвращаем пустой результат")
            return []

        # Загружаем данные акций
        data = yf.download(
            tickers=" ".join(symbols),
            period="1d",
            group_by="ticker",
            progress=False
        )
        logger.info("Данные акций успешно загружены с Yahoo Finance")

        # Формируем результат
        result = [
            {"stock": symbol, "price": round(float(data[symbol]["Close"][-1]), 2)}
            for symbol in symbols
            if symbol in data and not data[symbol]["Close"].empty
        ]

        logger.info(f"Успешно сформирован список цен акций: {result}")
        return result

    except Exception as e:
        logger.error(f"Ошибка при получении данных акций: {str(e)}", exc_info=True)
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
