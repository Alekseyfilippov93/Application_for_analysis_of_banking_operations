import pytest
from unittest.mock import patch
from datetime import datetime
from src.utils import get_time_for_greeting, get_date_time


# Тесты для get_time_for_greeting
class TestGreeting:
    @pytest.mark.parametrize(
        "hour, expected_greeting",
        [
            (5, "Доброе утро"),  # Утро (5:00)
            (11, "Доброе утро"),  # Утро (11:59)
            (12, "Добрый день"),  # День (12:00)
            (17, "Добрый день"),  # День (17:59)
            (18, "Добрый вечер"),  # Вечер (18:00)
            (21, "Добрый вечер"),  # Вечер (21:59)
            (22, "Добрый ночи"),  # Ночь (22:00)
            (4, "Добрый ночи"),  # Ночь (4:59)
        ],
    )
    def test_greeting_based_on_time(self, hour, expected_greeting):
        """Проверяем, что приветствие зависит от времени суток."""
        with patch("datetime.datetime") as mock_datetime:
            mock_datetime.now.return_value.hour = hour
            assert get_time_for_greeting() == expected_greeting


# Тесты для get_date_time
class TestDateTimeConversion:
    @pytest.mark.parametrize(
        "input_date, expected_output",
        [
            # Проверка стандартного формата
            (
                "2024-04-15 14:30:00",
                ["01.04.2024 14:30:00", "15.04.2024 14:30:00"],
            ),
            # Проверка другого месяца
            (
                "2023-12-31 23:59:59",
                ["01.12.2023 23:59:59", "31.12.2023 23:59:59"],
            ),
            # Проверка високосного года
            (
                "2020-02-29 00:00:00",
                ["01.02.2020 00:00:00", "29.02.2020 00:00:00"],
            ),
        ],
    )
    def test_date_conversion(self, input_date, expected_output):
        """Проверяем преобразование даты в период (начало месяца + текущая дата)."""
        result = get_date_time(input_date)
        assert result == expected_output

    def test_custom_date_format(self):
        """Проверяем работу с нестандартным форматом даты."""
        custom_date = "15/04/2024 14-30-00"
        custom_format = "%d/%m/%Y %H-%M-%S"
        expected_output = ["01.04.2024 14:30:00", "15.04.2024 14:30:00"]

        result = get_date_time(custom_date, custom_format)
        assert result == expected_output

    def test_invalid_date_raises_error(self):
        """Проверяем, что некорректная дата вызывает ошибку."""
        with pytest.raises(ValueError):
            get_date_time("2024-04-15 25:00:00")  # Неправильный час
