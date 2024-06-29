# This is a sample Python script.
import requests

import urllib.parse
import html

from datetime import datetime
import pytz


def time_until(target_datetime_str, timezone_str='Asia/Almaty'):
    # Определяем целевую дату и время в указанной временной зоне
    target_datetime = datetime.strptime(target_datetime_str, "%d.%m.%Y %H:%M")

    # Устанавливаем временную зону
    target_timezone = pytz.timezone(timezone_str)
    target_datetime = target_timezone.localize(target_datetime)

    # Определяем текущее время в той же временной зоне
    current_datetime = datetime.now(target_timezone)

    # Рассчитываем разницу
    remaining_time = target_datetime - current_datetime
    print(remaining_time)

    return str(remaining_time).split('.')[0]


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
        print(flight)
        path_from = flight['path']['origin']['originEn']
        path_to = flight['path']['destination']['destinationEn']
        flightNumber = flight['flightNumber'] #Номер рейса
        stad = flight['stad'] #Вылет по рассписанию
        etad = flight['etad'] #Вылет по факту
        time_left = time_until(etad)
        atad = flight['atad'] #Прилет по факту
        remark = flight['remark']['remarkEn'] #Задержка рейса на столько то часов
        gate = flight['gate'] #Терминал посадки/высадки
        carousel = flight['carousel'] #Багажная лента

        txt = (f'Вылет из {path_from} в {path_to}\n'
               f'Рейс {flightNumber}\n'
               f'Время вылета _по расп.: {stad}\n'
               f'Время вылета _по факту: {etad}\n'
               f'До вылета: {time_left}\n'
               f'Время прилета по факту: {atad}\n'
               f'Задержка рейса: {remark}\n'
               f'Терминал {gate}\n'
               f'Багажная лента: {carousel}')

        print(txt)



def ura_to_ala():
    date = '2024-06-29'
    destination = 'ОРАЛ'
    url = f'https://alaport.com/Home/searchFlights?flightLeg=ARR&date={date}&destination={destination}&airline=FLY%20ARYSTAN&requestRawUrl=%2Fru-RU%2Fflights-ru%2Farrival-flights-ru'
    raspars_data_alaport(url)








# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    ura_to_ala()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
