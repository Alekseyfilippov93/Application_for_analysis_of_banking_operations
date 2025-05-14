import logging
import pandas as pd
from typing import Optional, Callable, Any
import json
from datetime import datetime, timedelta
from pathlib import Path

# Настройка логирования
logging.basicConfig(filename="app.log", level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

PATH_TO_FILE = Path(__file__).parent.parent / "data" / "operations.xlsx"


def report_to_file(filename: Optional[str] = None):
    """Декоратор для сохранения результатов в JSON."""

    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs) -> Any:
            logger.info(f"Начало выполнения функции {func.__name__}")
            logger.debug(f"Аргументы функции: args={args}, kwargs={kwargs}")

            try:
                result = func(*args, **kwargs)
                logger.info(f"Функция {func.__name__} успешно выполнена")
            except Exception as e:
                logger.error(f"Ошибка в функции {func.__name__}: {str(e)}")
                raise

            file_to_save = filename or f"report_{func.__name__}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            logger.debug(f"Подготовка к сохранению отчета: {file_to_save}")

            try:
                if isinstance(result, pd.DataFrame):
                    logger.debug("Результат является DataFrame, сохраняем в JSON")
                    # Сохраняем только нужные колонки
                    result.to_json(file_to_save, orient="records", indent=4, force_ascii=False)
                else:
                    logger.debug("Результат не является DataFrame, сохраняем как обычный JSON")
                    with open(file_to_save, "w", encoding="utf-8") as f:
                        json.dump(result, f, indent=4, ensure_ascii=False)
                logger.info(f"Отчет успешно сохранен: {file_to_save}")
            except Exception as e:
                logger.error(f"Ошибка при сохранении отчета {file_to_save}: {e}")
                raise

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
    logger.info(f"Запуск spending_by_category для категории '{category}' и даты {date}")

    # Проверка обязательных колонок
    required_columns = {"Дата операции", "Категория", "Сумма операции"}
    if not required_columns.issubset(transactions.columns):
        missing = required_columns - set(transactions.columns)
        error_msg = f"Отсутствуют колонки: {missing}"
        logger.error(error_msg)
        raise ValueError(error_msg)

    # Обработка дат
    try:
        target_date = pd.to_datetime(date, dayfirst=True) if date else datetime.now()
        three_months_ago = target_date - pd.DateOffset(months=3)
        logger.debug(f"Фильтрация данных за период с {three_months_ago} по {target_date}")
    except Exception as e:
        logger.error(f"Ошибка обработки дат: {str(e)}")
        raise

    # Конвертация дат в DataFrame
    try:
        transactions["Дата операции"] = pd.to_datetime(transactions["Дата операции"], dayfirst=True, errors="coerce")
        logger.debug("Конвертация дат выполнена успешно")
    except Exception as e:
        logger.error(f"Ошибка конвертации дат: {str(e)}")
        raise

    # Фильтрация
    try:
        mask = (
            (transactions["Категория"] == category)
            & (transactions["Дата операции"] >= three_months_ago)
            & (transactions["Дата операции"] <= target_date)
            & (transactions["Сумма операции"] < 0)  # Только траты (отрицательные значения)
        )

        filtered_count = mask.sum()
        logger.debug(f"Найдено {filtered_count} записей, соответствующих критериям")
    except Exception as e:
        logger.error(f"Ошибка при фильтрации данных: {str(e)}")
        raise

    # Выбираем нужные колонки
    try:
        result = transactions.loc[mask, ["Дата операции", "Категория", "Сумма операции", "Описание"]].copy()

        # Конвертируем сумму в абсолютные значения
        result["Сумма операции"] = result["Сумма операции"].abs()

        logger.info(f"Успешно сформирован отчет с {len(result)} записями")
        return result.sort_values("Дата операции", ascending=False)
    except Exception as e:
        logger.error(f"Ошибка при формировании результата: {str(e)}")
        raise
