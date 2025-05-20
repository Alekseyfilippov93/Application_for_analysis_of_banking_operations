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
@pytest.fixture
def transactions():
    return pd.DataFrame(
        [
            {"Дата операции": "01.03.2025", "Категория": "Продукты", "Сумма операции": -1200, "Описание": "Магазин А"},
            {"Дата операции": "01.04.2025", "Категория": "Продукты", "Сумма операции": -500, "Описание": "Магазин Б"},
            {"Дата операции": "01.01.2025", "Категория": "Продукты", "Сумма операции": -300, "Описание": "Магазин В"},
            {"Дата операции": "01.04.2025", "Категория": "Кафе", "Сумма операции": -200, "Описание": "Кофейня"},
            {"Дата операции": "01.04.2025", "Категория": "Продукты", "Сумма операции": 1000, "Описание": "Возврат"},
        ]
    )


def test_spending_by_category_basic(transactions):
    result = spending_by_category(transactions, "Продукты", date="30.04.2025")
    assert len(result) == 2
    assert all(result["Категория"] == "Продукты")
    assert all(result["Сумма операции"] > 0)


def test_spending_by_category_empty(transactions):
    result = spending_by_category(transactions, "Транспорт", date="30.04.2025")
    assert result.empty


def test_spending_by_category_missing_column():
    df = pd.DataFrame(
        {
            "Дата операции": ["01.01.2025"],
            "Категория": ["Продукты"],
            # "Сумма операции" отсутствует
        }
    )
    with pytest.raises(ValueError):
        spending_by_category(df, "Продукты")


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
