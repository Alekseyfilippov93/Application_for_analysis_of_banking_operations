from collections import defaultdict
from datetime import datetime


def analyze_cashback(transactions, year, month):
    """
    Анализ выгодности категорий повышенного кешбэка.
    Возвращает данные за указанный месяц и год в виде списка словарей.
    """
    filtered = filter(
        lambda x: datetime.strptime(x["Дата операции"], "%d.%m.%Y %H:%M:%S").year == year
                  and datetime.strptime(x["Дата операции"], "%d.%m.%Y %H:%M:%S").month == month,
        transactions
    )
    cashback_summary = defaultdict(float)
    for txn in filtered:
        category = txn["Категория"]
        cashback = txn["Кэшбэк"]
        cashback_summary[category] += cashback
    return dict(cashback_summary)
