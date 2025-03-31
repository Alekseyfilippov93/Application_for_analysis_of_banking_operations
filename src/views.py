from src.utils import get_time_for_greeting, get_date_time
import json


def main(date):
    '''
    Функция для страницы «Главная» принимает на вход строку с датой и временем в формате
    YYYY-MM-DD HH:MM:SS и возвращающую JSON-ответ
    '''
    greeting = get_time_for_greeting()
    time_period: str = get_date_time(date)
    data = {
        "greeting": greeting,
        "time_period": time_period
    }
    json_data = json.dumps(data, ensure_ascii=False, indent=4)
    return json_data


if __name__ == "__main__":
    print(main("2018-05-20 15:30:00"))
