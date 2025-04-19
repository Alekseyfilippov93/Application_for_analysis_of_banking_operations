from collections import defaultdict


def analyze_cashback(transactions, year, month):
    """
    Анализ выгодности категорий повышенного кешбэка.
    Возвращает данные за указанный месяц и год в виде списка словарей.
    """
    filtered = filter(lambda x: x["date"].year == year and x["date"].month == month, transactions)
    cashback_summary = defaultdict(float)
    for txn in filtered:
        category = txn["category"]
        cashback = txn["cashback"]
        cashback_summary[category] += cashback
    return dict(cashback_summary)
