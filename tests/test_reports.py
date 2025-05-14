import pytest
import pandas as pd
import json
from unittest.mock import patch
import os

# Импортируем тестируемые функции
from src.reports import spending_by_category, report_to_file


# Фикстуры для тестов
@pytest.fixture
def sample_transactions():
    """Фикстура с тестовыми данными транзакций"""
    data = {
        "Дата операции": [
            "01.01.2023",
            "15.01.2023",
            "01.02.2023",
            "15.02.2023",
            "01.03.2023",
            "15.03.2023",
            "01.04.2023",
        ],
        "Категория": ["Еда", "Транспорт", "Еда", "Развлечения", "Еда", "Транспорт", "Еда"],
        "Сумма операции": [-500, -200, -300, -1000, -400, -150, -600],
        "Описание": ["Обед", "Такси", "Продукты", "Кино", "Ужин", "Метро", "Кафе"],
    }
    return pd.DataFrame(data)


@pytest.fixture
def temp_json_file(tmp_path):
    """Фикстура для временного JSON файла"""
    return tmp_path / "temp_report.json"


# Тесты для spending_by_category
def test_spending_by_category_success(sample_transactions, temp_json_file):
    """Тест успешного выполнения функции"""
    with patch.object(spending_by_category, "__wrapped__", return_file=False):
        result = spending_by_category(sample_transactions, "Еда")

    assert isinstance(result, pd.DataFrame)
    assert len(result) == 4
    assert all(result["Категория"] == "Еда")
    assert all(result["Сумма операции"] > 0)


def test_spending_by_category_date_filter(sample_transactions):
    """Тест фильтрации по дате"""
    with patch.object(spending_by_category, "__wrapped__", return_file=False):
        result = spending_by_category(sample_transactions, "Еда", "01.03.2023")

    assert len(result) == 3  # Только операции до 01.03.2023


def test_spending_by_category_missing_columns(sample_transactions):
    """Тест обработки отсутствия обязательных колонок"""
    with pytest.raises(ValueError):
        spending_by_category(sample_transactions.drop(columns=["Категория"]), "Еда")


def test_spending_by_category_no_spending(sample_transactions):
    """Тест случая, когда нет трат по категории"""
    with patch.object(spending_by_category, "__wrapped__", return_file=False):
        result = spending_by_category(sample_transactions, "Развлечения")
    assert len(result) == 1


# Тесты для декоратора report_to_file
def test_report_to_file_dataframe(temp_json_file, sample_transactions):
    """Тест сохранения DataFrame в файл"""

    @report_to_file(str(temp_json_file))
    def dummy_func():
        return sample_transactions

    result = dummy_func()

    assert os.path.exists(temp_json_file)
    assert isinstance(result, pd.DataFrame)

    with open(temp_json_file, "r") as f:
        data = json.load(f)
    assert len(data) == len(sample_transactions)


def test_report_to_file_dict(temp_json_file):
    """Тест сохранения словаря в файл"""
    test_data = {"key": "value", "numbers": [1, 2, 3]}

    @report_to_file(str(temp_json_file))
    def dummy_func():
        return test_data

    result = dummy_func()

    assert os.path.exists(temp_json_file)
    assert result == test_data

    with open(temp_json_file, "r") as f:
        data = json.load(f)
    assert data == test_data


def test_report_to_file_default_filename():
    """Тест генерации имени файла по умолчанию"""

    @report_to_file()
    def dummy_func():
        return {"test": 123}

    with patch("builtins.open") as mock_open:
        dummy_func()

    assert mock_open.call_args[0][0].startswith("report_dummy_func_")


def test_report_to_file_error_logging(caplog):
    """Тест логирования ошибок"""

    @report_to_file("test.json")
    def error_func():
        raise ValueError("Test error")

    with pytest.raises(ValueError):
        error_func()

    assert "Ошибка в функции error_func" in caplog.text


# Тесты для обработки ошибок
def test_invalid_date_format(sample_transactions):
    """Тест обработки неверного формата даты"""
    with pytest.raises(Exception):
        spending_by_category(sample_transactions, "Еда", "invalid_date")


def test_empty_dataframe():
    """Тест с пустым DataFrame"""
    with patch.object(spending_by_category, "__wrapped__", return_file=False):
        result = spending_by_category(pd.DataFrame(), "Еда")
    assert len(result) == 0


# Проверка логирования
def test_function_logging(caplog, sample_transactions):
    """Тест корректности логирования"""
    with patch.object(spending_by_category, "__wrapped__", return_file=False):
        spending_by_category(sample_transactions, "Еда")

    assert "Запуск spending_by_category для категории 'Еда'" in caplog.text
    assert "Успешно сформирован отчет" in caplog.text
