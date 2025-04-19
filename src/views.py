from src.utils import (
    get_time_for_greeting,
    calculate_total_expenses,
    top_transactions_5,
    get_cur_rate,
    get_stock_prices,
)


def get_main_page(date_str):
    return {
        "greeting": get_time_for_greeting(date_str),
        "cards": calculate_total_expenses(),
        "top_transactions": top_transactions_5(),
        "currency_rates": get_cur_rate(),
        "stock_prices": get_stock_prices(),
    }
