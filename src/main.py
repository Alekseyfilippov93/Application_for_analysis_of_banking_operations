import pandas as pd

from config import PATH_HOME
from views import get_main_page
from src.services import analyze_cashback
from src.reports import spending_by_category
import os

DATA_FILE = os.path.join(PATH_HOME, "data", "operations.xlsx")


def main():
    # Вызов функции веб-страницы
    web_page_result = get_main_page("2021-12-17 05:12:31")
    print(web_page_result)

    # Загрузка данных и преобразование в список словарей
    all_transactions_df = pd.read_excel(DATA_FILE)
    all_transactions_as_list = all_transactions_df.to_dict(orient="records")

    # Вызов функции сервиса
    service_result = analyze_cashback(all_transactions_as_list, 2021, 11)
    print(service_result)

    # Вызов функции отчёта
    report_result = spending_by_category(all_transactions_df, "Фастфуд", "17.12.2021")
    print(report_result)


if __name__ == "__main__":
    main()
