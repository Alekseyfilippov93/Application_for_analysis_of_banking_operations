import json
from unittest.mock import patch, MagicMock
import pytest
import pandas as pd

# Тестируемый модуль
from src.views import get_main_page


@pytest.fixture
def mock_operations_df():
    """Фикстура с тестовыми данными операций"""
    data = {
        "Дата операции": ["2023-01-01", "2023-01-15", "2023-02-01"],
        "Сумма операции": [-1000, -500, 2000],
        "Категория": ["Еда", "Транспорт", "Зарплата"],
        "Описание": ["Продукты", "Такси", "ЗП"],
    }
    return pd.DataFrame(data)


@pytest.fixture
def mock_user_settings(tmp_path):
    """Фикстура с моком user_settings.json"""
    settings = {"user_currencies": ["USD", "EUR"]}
    file_path = tmp_path / "user_settings.json"
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(settings, f)
    return file_path


def test_get_main_page_success(mock_operations_df, mock_user_settings):
    """Тест успешного выполнения функции"""
    with patch("pandas.read_excel", return_value=mock_operations_df), patch(
        "os.path.abspath", return_value=str(mock_user_settings.parent)
    ), patch("your_module.get_time_for_greeting", return_value="Добрый день"), patch(
        "your_module.calculate_total_expenses", return_value={"total": 1500}
    ), patch(
        "your_module.top_transactions_5", return_value=[{"amount": 1000}]
    ), patch(
        "your_module.get_cur_rate", return_value={"USD": 75.0}
    ), patch(
        "your_module.get_stock_prices", return_value={"AAPL": 150}
    ), patch(
        "your_module.filter_date_operations", side_effect=lambda df, _: df
    ), patch(
        "your_module.convert_timestamps_to_strings", side_effect=lambda df: df
    ):
        result = get_main_page("2023-01-01")
        data = json.loads(result)

        assert data["greeting"] == "Добрый день"
        assert data["cards"]["total"] == 1500
        assert len(data["top_transactions"]) == 1
        assert data["currency_rates"]["USD"] == 75.0
        assert data["stock_prices"]["AAPL"] == 150


def test_get_main_page_file_not_found():
    """Тест обработки отсутствия файла операций"""
    with patch("pandas.read_excel", side_effect=FileNotFoundError("File not found")):
        with pytest.raises(FileNotFoundError):
            get_main_page("2023-01-01")


def test_get_main_page_invalid_json(tmp_path):
    """Тест обработки невалидного JSON"""
    invalid_json = tmp_path / "invalid.json"
    invalid_json.write_text("{invalid}")

    with patch("pandas.read_excel", return_value=pd.DataFrame()), patch("os.path.abspath", return_value=str(tmp_path)):
        with pytest.raises(json.JSONDecodeError):
            get_main_page("2023-01-01")


def test_get_main_page_empty_dataframe():
    """Тест с пустым DataFrame"""
    with patch("pandas.read_excel", return_value=pd.DataFrame()), patch("os.path.abspath"), patch(
        "your_module.get_time_for_greeting"
    ), patch("your_module.calculate_total_expenses", return_value={}), patch(
        "your_module.top_transactions_5", return_value=[]
    ), patch(
        "your_module.get_cur_rate", return_value={}
    ), patch(
        "your_module.get_stock_prices", return_value={}
    ), patch(
        "your_module.filter_date_operations"
    ), patch(
        "your_module.convert_timestamps_to_strings"
    ):
        result = get_main_page("2023-01-01")
        data = json.loads(result)

        assert data["top_transactions"] == []
        assert data["cards"] == {}


def test_get_main_page_missing_columns(mock_operations_df, mock_user_settings):
    """Тест с DataFrame без нужных колонок"""
    bad_df = mock_operations_df.drop(columns=["Сумма операции"])

    with patch("pandas.read_excel", return_value=bad_df), patch(
        "os.path.abspath", return_value=str(mock_user_settings.parent)
    ), patch("your_module.filter_date_operations", side_effect=lambda df, _: df):
        with pytest.raises(KeyError):
            get_main_page("2023-01-01")


@pytest.mark.parametrize("date", ["2023-01-01", "2023-02-15", "2023-12-31"])
def test_get_main_page_with_different_dates(date, mock_operations_df, mock_user_settings):
    """Параметризованный тест с разными датами"""
    with patch("pandas.read_excel", return_value=mock_operations_df), patch(
        "os.path.abspath", return_value=str(mock_user_settings.parent)
    ), patch("your_module.get_time_for_greeting"), patch(
        "your_module.calculate_total_expenses", return_value={}
    ), patch(
        "your_module.top_transactions_5", return_value=[]
    ), patch(
        "your_module.get_cur_rate", return_value={}
    ), patch(
        "your_module.get_stock_prices", return_value={}
    ), patch(
        "your_module.filter_date_operations", side_effect=lambda df, _: df
    ), patch(
        "your_module.convert_timestamps_to_strings", side_effect=lambda df: df
    ):
        result = get_main_page(date)
        data = json.loads(result)
        assert isinstance(data, dict)
