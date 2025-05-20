import pytest
import pandas as pd
from src.utils import (
    get_time_for_greeting,
    get_date_time,
    calculate_expenses_by_cards,
    top_transactions_5,
    convert_timestamps_to_strings,
    filter_date_operations,
)

from datetime import datetime


def test_get_time_for_greeting():
    greeting = get_time_for_greeting()
    assert greeting in ["Доброе утро", "Добрый день", "Добрый вечер", "Добрый ночи"]


@pytest.mark.parametrize(
    "input_date, expected",
    [
        ("2025-05-10 14:30:00", ["01.05.2025 14:30:00", "10.05.2025 14:30:00"]),
        ("2023-01-01 00:00:00", ["01.01.2023 00:00:00", "01.01.2023 00:00:00"]),
    ],
)
def test_get_date_time(input_date, expected):
    assert get_date_time(input_date) == expected


@pytest.mark.parametrize(
    "cashback, expected_cashback",
    [
        (False, 0.0),
        (True, 10.0),
    ],
)
def test_calculate_expenses_by_cards(cashback, expected_cashback):
    data = pd.DataFrame(
        {
            "Статус": ["OK", "OK"],
            "Сумма операции": [-100.0, -200.0],
            "Номер карты": ["1234", "1234"],
            "Бонусы (включая кэшбэк)": [5.0, 5.0],
        }
    )
    result = calculate_expenses_by_cards(data, cashback=cashback)
    assert len(result) == 1
    assert result[0]["total_spent"] == 300.0
    assert result[0]["cashback"] == expected_cashback


def test_top_transactions_5():
    df = pd.DataFrame(
        {
            "Дата платежа": ["2025-05-01", "2025-05-02", "2025-05-03", "2025-05-04", "2025-05-05", "2025-05-06"],
            "Категория": ["A", "B", "C", "D", "E", "F"],
            "Сумма платежа": [100, 500, 300, 400, 200, 50],
            "Описание": ["a", "b", "c", "d", "e", "f"],
        }
    )
    top5 = top_transactions_5(df)
    assert len(top5) == 5
    assert top5[0]["amount"] == 500  # Самая большая сумма


def test_convert_timestamps_to_strings():
    df = pd.DataFrame({"дата": [pd.Timestamp("2025-05-01 12:00:00"), pd.Timestamp("2025-05-02 13:00:00")]})
    result = convert_timestamps_to_strings(df)
    assert result["дата"].iloc[0] == "2025-05-01 12:00:00"


def test_filter_date_operations():
    df = pd.DataFrame(
        {
            "Дата операции": ["01.05.2025 14:00:00", "10.05.2025 15:00:00", "01.04.2025 15:00:00"],
            "Сумма": [100, 200, 300],
        }
    )
    result = filter_date_operations(df, "2025-05-20 23:59:59")
    assert len(result) == 2