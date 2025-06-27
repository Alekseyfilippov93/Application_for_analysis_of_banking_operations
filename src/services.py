import logging
from collections import defaultdict
from datetime import datetime

# Настройка логирования
logging.basicConfig(filename="app.log", level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def analyze_cashback(transactions, year, month):
    """
    Анализ выгодности категорий повышенного кешбэка.
    Возвращает данные за указанный месяц и год в виде списка словарей.
    """
    logger.info(f"Анализ кешбэка за {month}.{year}")

    if not transactions:
        logger.warning("Получен пустой список транзакций")
        return {}

    cashback_summary = defaultdict(float)
    invalid_count = 0

    for txn in transactions:
        try:
            txn_date = datetime.strptime(txn["Дата операции"], "%d.%m.%Y %H:%M:%S")
            if txn_date.year == year and txn_date.month == month:
                category = txn["Категория"]
                cashback = float(txn["Кэшбэк"])
                cashback_summary[category] += cashback
        except (KeyError, ValueError) as e:
            invalid_count += 1

    if invalid_count > 0:
        logger.warning(f"Пропущено {invalid_count} транзакций с ошибками")

    result = dict(cashback_summary)
    logger.info(f"Найдено {len(result)} категорий с кешбэком")

    return result
