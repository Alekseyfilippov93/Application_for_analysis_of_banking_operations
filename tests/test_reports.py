import pytest
from unittest.mock import patch, mock_open
import pandas as pd
from datetime import datetime, timedelta
import json
from pathlib import Path
from src.reports import spending_by_category, report_to_file


# Фикстура для тестовых данных
@pytest.fixture
def sample_transactions():
    return pd.DataFrame(
        {
            "Дата операции": ["01.01.2024", "15.02.2024", "10.03.2024", "05.04.2024"],
            "Категория": ["Еда", "Транспорт", "Еда", "Развлечения"],
            "Сумма операции": [-500, -200, -300, -1000],
            "Описание": ["Покупка еды", "Такси", "Ресторан", "Кино"],
        }
    )


# Фикстура для даты (чтобы тесты не зависели от текущей даты)
@pytest.fixture
def fixed_date():
    return "10.04.2024"


# Тесты для spending_by_category
class TestSpendingByCategory:
    def test_required_columns_missing(self, sample_transactions):
        """
        Проверяем, что функция вызывает ошибку, если не хватает колонок.
        """
        with pytest.raises(ValueError, match="Отсутствуют колонки:"):
            spending_by_category(sample_transactions.drop(columns=["Категория"]), "Еда")

    def test_filter_by_category(self, sample_transactions, fixed_date):
        """
        Проверяем фильтрацию по категории.
        """
        result = spending_by_category(sample_transactions, "Еда", fixed_date)

        # Должны остаться только две записи с категорией "Еда"
        assert len(result) == 2
        assert all(result["Категория"] == "Еда")

        # Даты должны быть в правильном порядке (сначала новые)
        assert result["Дата операции"].iloc[0] == pd.to_datetime("10.03.2024", dayfirst=True)

    def test_only_negative_values(self, sample_transactions, fixed_date):
        """
        Проверяем, что берутся только отрицательные суммы.
        """
        # Добавляем положительную операцию
        df = sample_transactions.copy()
        df.loc[len(df)] = ["01.04.2024", "Еда", 500, "Бонус"]

        result = spending_by_category(df, "Еда", fixed_date)
        assert len(result) == 2  # Бонус не должен попасть в отчёт

    def test_date_filtering(self, sample_transactions, fixed_date):
        """Проверяем, что берутся только последние 3 месяца."""
        # Добавляем старую запись (больше 3 месяцев назад)
        df = sample_transactions.copy()
        df.loc[len(df)] = ["01.10.2023", "Еда", -100, "Старая покупка"]

        result = spending_by_category(df, "Еда", fixed_date)
        assert len(result) == 2  # Старая запись не должна попасть


# Тесты для декоратора report_to_file
class TestReportToFile:
    @patch("builtins.open", new_callable=mock_open)
    @patch("json.dump")
    @patch("pandas.DataFrame.to_json")
    def test_save_json_report(self, mock_to_json, mock_json_dump, mock_file, sample_transactions):
        """Проверяем сохранение отчёта в JSON."""

        # Декорируем функцию вручную (без @)
        decorated_func = report_to_file("test_report.json")(lambda: {"test": 123})


        # Проверяем, что файл пытались сохранить
        mock_file.assert_called_once_with("test_report.json", "w", encoding="utf-8")
        mock_json_dump.assert_called_once_with({"test": 123}, mock_file(), indent=4, ensure_ascii=False)

    @patch("pandas.DataFrame.to_json")
    def test_save_dataframe_report(self, mock_to_json, sample_transactions):
        """Проверяем сохранение DataFrame в JSON."""

        # Декорируем spending_by_category
        decorated_func = report_to_file("test_report.json")(spending_by_category)

        # Вызываем функцию
        result = decorated_func(sample_transactions, "Еда")

    @patch("logging.error")
    @patch("builtins.open", side_effect=Exception("Ошибка записи"))
    def test_save_error_handling(self, mock_open, mock_log_error):
        """Проверяем обработку ошибок при сохранении."""

        decorated_func = report_to_file("test_report.json")(lambda: {"test": 123})
        decorated_func()

        # Проверяем, что ошибка залогирована
        mock_log_error.assert_called_once_with("Ошибка сохранения: Ошибка записи")
