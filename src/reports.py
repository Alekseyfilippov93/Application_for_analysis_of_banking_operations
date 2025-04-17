import pandas as pd
from typing import Optional, Callable, Any
import json
from datetime import datetime, timedelta
import logging
from pathlib import Path

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PATH_TO_FILE = Path(__file__).parent.parent / "data" / "operations.xlsx"


def report_to_file(filename: Optional[str] = None):
    """Декоратор для сохранения результатов в JSON."""

    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs) -> Any:
            result = func(*args, **kwargs)

            file_to_save = filename or f"report_{func.__name__}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

            try:
                if isinstance(result, pd.DataFrame):
                    # Сохраняем только нужные колонки
                    result.to_json(file_to_save, orient="records", indent=4, force_ascii=False)
                else:
                    with open(file_to_save, "w", encoding="utf-8") as f:
                        json.dump(result, f, indent=4, ensure_ascii=False)
                logger.info(f"Отчет сохранен: {file_to_save}")
            except Exception as e:
                logger.error(f"Ошибка сохранения: {e}")

            return result

        return wrapper

    return decorator


@report_to_file("../data/Траты_по_категориям.json")
def spending_by_category(transactions: pd.DataFrame, category: str, date: Optional[str] = None) -> pd.DataFrame:
    """
    Фильтрует траты по категории за последние 3 месяца.
    Возвращает DataFrame с колонками:
    Дата операции, Категория, Сумма операции, Описание
    """

    # Проверка обязательных колонок
    required_columns = {"Дата операции", "Категория", "Сумма операции"}
    if not required_columns.issubset(transactions.columns):
        missing = required_columns - set(transactions.columns)
        raise ValueError(f"Отсутствуют колонки: {missing}")

    # Обработка дат
    target_date = pd.to_datetime(date, dayfirst=True) if date else datetime.now()
    three_months_ago = target_date - pd.DateOffset(months=3)

    # Конвертация дат в DataFrame
    transactions["Дата операции"] = pd.to_datetime(transactions["Дата операции"], dayfirst=True, errors="coerce")

    # Фильтрация
    mask = (
        (transactions["Категория"] == category)
        & (transactions["Дата операции"] >= three_months_ago)
        & (transactions["Дата операции"] <= target_date)
        & (transactions["Сумма операции"] < 0)  # Только траты (отрицательные значения)
    )

    # Выбираем нужные колонки
    result = transactions.loc[mask, ["Дата операции", "Категория", "Сумма операции", "Описание"]].copy()

    # Конвертируем сумму в абсолютные значения
    result["Сумма операции"] = result["Сумма операции"].abs()

    return result.sort_values("Дата операции", ascending=False)
