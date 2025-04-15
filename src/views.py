from src.utils import get_time_for_greeting, get_date_time
import json
import os
from typing import List, Any
import pandas as pd
from dotenv import load_dotenv
import yfinance as yf
import requests

load_dotenv()
from src.utils import PATH_TO_FILE


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
    # Загружаем Excel-файл
    df = pd.read_excel(PATH_TO_FILE)

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
        return round(net_expenses, 2)


def top_transactions_5(df: List[dict]) -> List[dict]:
    """Функция возвращает топ 5 транзакций"""
    df = pd.read_excel(PATH_TO_FILE)
    df.sort(key=lambda x: x["Сумма операции"], reverse=True)
    return df[:5]


API_KEY = os.getenv("API_KEY")


def get_cur_rate(currency: str) -> Any:
    """Функция для получения курса валют."""
    url = f"https://api.apilayer.com/exchangerates_data/latest?symbols=RUB&base={currency}"
    response = requests.get(url, headers={"apikey": API_KEY}, timeout=40)
    response_data = json.loads(response.text)
    return response_data["rates"]["RUB"]


def get_stock_prices(symbols=["AAPL", "AMZN", "GOOG", "MSFT", "TSLA"]):
    """
    Получает текущие цены акций через Yahoo Finance
    """
    try:
        data = yf.download(tickers=" ".join(symbols), period="1d", group_by="ticker", progress=False)

        return {
            "stock_prices": [
                {"stock": symbol, "price": round(float(data[symbol]["Close"][-1]), 2)}
                for symbol in symbols
                if symbol in data and not data[symbol]["Close"].empty
            ]
        }
    except Exception:
        return {"stock_prices": []}
