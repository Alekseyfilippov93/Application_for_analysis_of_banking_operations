import pandas as pd
from src.utils import PATH_TO_FILE


def analize_chashbek(data_file: str, year: int, month: int):
    '''
    Анализ выгодности категорий повышенного кешбэка.
    Возвращает данные за указанный месяц и год в виде списка словарей.
    '''
    print(data_file)
    try:
        df = pd.read_excel(data_file)
    except Exception as e:
        return {}  # Возвращаем пустой DataFrame

    # Преобразование даты
    df['Дата операции'] = pd.to_datetime(df['Дата операции'].str.strip(), dayfirst=True, errors='coerce')

    # Фильтр по году и месяцу
    mask = ((df['Дата операции'].dt.year == year) & (df['Дата операции'].dt.month == month))
    filter_date = df[mask]

    return filter_date.to_dict('dict')


if __name__ == "__main__":
    result = analize_chashbek(PATH_TO_FILE, 2019, 12)
    print(result)
