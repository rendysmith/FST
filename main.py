# This is a sample Python script.
import requests
from bs4 import BeautifulSoup

import urllib.parse
import html

from datetime import datetime
import pytz

flightNs = ['7166', '7167', '1722', '1721']


def time_until(target_datetime_str, timezone_str='Asia/Almaty'):
    # Определяем целевую дату и время в указанной временной зоне
    try:
        target_datetime = datetime.strptime(target_datetime_str, "%d.%m.%Y %H:%M")
    except ValueError as VE:
        target_datetime_str += f".{str(datetime.now().year)}"
        #print(target_datetime_str)
        target_datetime = datetime.strptime(target_datetime_str, "%H:%M %d.%m.%Y")

    # Устанавливаем временную зону
    target_timezone = pytz.timezone(timezone_str)
    target_datetime = target_timezone.localize(target_datetime)

    # Определяем текущее время в той же временной зоне
    current_datetime = datetime.now(target_timezone)

    # Рассчитываем разницу
    remaining_time = target_datetime - current_datetime
    return str(remaining_time).split('.')[0]


def calculate_time_difference(start, end):
    # Определяем формат даты и времени
    date_format = "%H:%M %d.%m"

    # Преобразуем строки в объекты datetime
    start_datetime = datetime.strptime(start, date_format)
    end_datetime = datetime.strptime(end, date_format)

    # Рассчитываем разницу между датами
    difference = end_datetime - start_datetime

    # Получаем количество часов и минут
    total_seconds = int(difference.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60

    return f"{hours}:{minutes:02d}"

def decode_string(encoded_str):
    # Декодирование URL-encoded строки
    url_decoded = urllib.parse.unquote(encoded_str)
    # Декодирование HTML-encoded строки
    html_decoded = html.unescape(url_decoded)
    return html_decoded

def raspars_data_alaport(url):
    r = requests.get(url).json()
    flights = r['data']['flights']
    for flight in flights:
        #print(flight)
        path_from = flight['path']['origin']['originEn']
        path_to = flight['path']['destination']['destinationEn']
        airlineIata = flight['airlineIata']
        flightNumber = flight['flightNumber'] #Номер рейса

        if any(flightN in flightNumber for flightN in flightNs):
            stad = flight['stad'] #Вылет по рассписанию
            etad = flight['etad'] #Вылет по факту
            time_left = time_until(etad)
            atad = flight['atad'] #Прилет по факту
            remark = flight['remark']['remarkEn'] #Задержка рейса на столько то часов
            gate = flight['gate'] #Терминал посадки/высадки
            carousel = flight['carousel'] #Багажная лента

            txt = (f'Аэропорт ALA\n'
                   f'Вылет из {path_from} в {path_to}\n'
                   f'Рейс: {airlineIata}-{flightNumber}\n'
                   f'Время вылета _по расп.: {stad}\n'
                   f'Время вылета _по факту: {etad}\n'
                   f'До вылета: {time_left}\n'
                   f'Время прилета по факту: {atad}\n'
                   f'Задержка рейса: {remark}\n'
                   f'Терминал {gate}\n'
                   f'Багажная лента: {carousel}')

            print(txt)

def raspars_data_uraport(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    tables = soup.find_all('a', class_='table-flex__row table-flex__row--link align-center')
    for table in tables:
        # print(table)
        flightNumber = table.find('div', class_='table-flex__td table-flex__td--type2').text.strip()
        # print(flightNumber)

        if any(flightN in flightNumber for flightN in flightNs):
            # print(table)
            path_from = 'Уральск URA'
            path_to = table.find('span', class_='table-flex__no-wrap').text.split()
            path_to = ' '.join(path_to)

            stad = table.find('div', class_='table-flex__td table-flex__td--type1').text.split()
            stad = ' '.join(stad)
            # print(stad)

            etad = table.find('div', class_='table-flex__td table-flex__td--type6').text.split()
            etad = ' '.join(etad)
            # print(etad)

            # print(stad, etad)
            atad = ''

            time_left = time_until(etad)

            remark = calculate_time_difference(stad, etad)

            gate = ''
            carousel = ''

            txt = (f'Аэропорт URA\n'
                   f'Вылет из {path_from} в {path_to}\n'
                   f'Рейс: {flightNumber}\n'
                   f'Время вылета _по расп.: {stad}\n'
                   f'Время вылета _по факту: {etad}\n'
                   f'До вылета: {time_left}\n'
                   f'Время прилета по факту: {atad}\n'
                   f'Задержка рейса: {remark}\n'
                   f'Терминал {gate}\n'
                   f'Багажная лента: {carousel}')

            print(txt)

def ura_to_ala_ala():
    date = '2024-07-12'
    destination = 'ОРАЛ'
    url = f'https://alaport.com/Home/searchFlights?flightLeg=ARR&date={date}&destination={destination}&airline=FLY%20ARYSTAN&requestRawUrl=%2Fru-RU%2Fflights-ru%2Farrival-flights-ru'
    raspars_data_alaport(url)

def ala_to_ura_ala():
    date = '2024-07-23'
    destination = 'ОРАЛ'
    url = f'https://alaport.com/Home/searchFlights?flightLeg=DEP&date={date}&destination={destination}&airline=FLY%20ARYSTAN&requestRawUrl=%2Fru-RU%2Fflights-ru%2Fdeparture-flights-ru'
    raspars_data_alaport(url)

def ura_to_ala_ura():
    urls = ['https://ura.aero/ru/board/', 'https://ura.aero/ru/board/?date=tomorrow']
    for url in urls:
        raspars_data_uraport(url)

def ala_to_ura_ura():
    urls = ['https://ura.aero/ru/board/?type=arr', 'https://ura.aero/ru/board/?type=arr&date=tomorrow']
    for url in urls:
        raspars_data_uraport(url)








# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    ura_to_ala_ala()
    ala_to_ura_ala()
    ura_to_ala_ura()
    ala_to_ura_ura()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
