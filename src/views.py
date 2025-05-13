import json
import os

import pandas as pd

from src.utils import (
    get_time_for_greeting,
    calculate_total_expenses,
    top_transactions_5,
    get_cur_rate,
    get_stock_prices,
    convert_timestamps_to_strings,
    filter_date_operations,
)


def get_main_page(date: str):
    """Возвращает JSON для главной Веб-страницы"""
    periodic_df = pd.read_excel("../data/operations.xlsx")
    periodic_df = filter_date_operations(periodic_df, date)
    periodic_df = convert_timestamps_to_strings(periodic_df)
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    file_json = os.path.join(project_root, "user_settings.json")
    with open(file_json, "r", encoding="utf-8") as f:
        currencies = json.load(f)["user_currencies"]
    result = {
        "greeting": get_time_for_greeting(),
        "cards": calculate_total_expenses(periodic_df),
        "top_transactions": top_transactions_5(periodic_df),
        "currency_rates": get_cur_rate(currencies),
        "stock_prices": get_stock_prices(),
    }
    return json.dumps(result, ensure_ascii=False)
