# This is a sample Python script.
import os.path

import requests
from bs4 import BeautifulSoup

import urllib.parse
import html
import re

from dotenv import dotenv_values
from datetime import datetime, timedelta
import pytz

import chardet

flightNs = ['7166', '7167', '1722', '1721']
dates = ['12.07', '13.07', '23.07']
#flightNs = ['7168', '882']


def get_dates():
    today = datetime.now().strftime('%d.%m')
    tomorrow = (datetime.now() + timedelta(days=1)).strftime('%d.%m')
    return today, tomorrow

# Пример использования:
today, tomorrow = get_dates()
print(today, tomorrow)

abspath = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(abspath, '.env')
env_vars = dotenv_values(env_path)
token = env_vars["TOKEN"]
channel_name = env_vars["CHANNEL_NAME"]

def send_telegram(text: str):
    url = "https://api.telegram.org/bot"
    url += token
    method = url + "/sendMessage"
    r = requests.post(method, data={
        "chat_id": channel_name,
        "text": text,
        "parse_mode": "HTML"
    })

    if r.status_code != 200:
        raise Exception("post_text error")


def extract_data(pattern, input_string):
    #pattern = r'fromName=(.*?)&toId=c'
    match = re.search(pattern, input_string)
    if match:
        return match.group(1)
    else:
        return None

def time_until(target_datetime_str, timezone_str='Asia/Almaty'):
    print(target_datetime_str)
    # Определяем целевую дату и время в указанной временной зоне
    try:
        target_datetime = datetime.strptime(target_datetime_str, "%d.%m.%Y %H:%M")
    except ValueError as VE:
        try:
            target_datetime_1 = target_datetime_str + f".{str(datetime.now().year)}"
            target_datetime = datetime.strptime(target_datetime_1, "%H:%M %d.%m.%Y")
        except:
            target_datetime_2 = target_datetime_str + f" {str(datetime.now().day)}.{str(datetime.now().month)}.{str(datetime.now().year)}"
            print(target_datetime_2)
            target_datetime = datetime.strptime(target_datetime_2, "%H:%M %d.%m.%Y")

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
        #print(flightNumber, type(flightNumber))

        if any(flightN in flightNumber for flightN in flightNs):
            stad = flight['stad'] #Вылет по рассписанию
            etad = flight['etad'] #Вылет по факту
            time_left = time_until(etad)
            atad = flight['atad'] #Прилет по факту
            remark = flight['remark']['remarkEn'] #Задержка рейса на столько то часов
            gate = flight['gate'] #Терминал посадки/высадки
            carousel = flight['carousel'] #Багажная лента

            if 'ARR' in url:
                st = 'прилета'

            elif "DEP" in url:
                st = 'вылета'

            if not any(date in [today, tomorrow] for date in dates):
                print("continue")
                continue

            txt = (f'🌐Аэропорт ALA\n'
                   f'🛫Вылет из {path_from} в {path_to}\n'
                   f'✈️Рейс: {airlineIata}-{flightNumber}\n'
                   f'💺Время {st} _по расп.: {stad}\n'
                   f'🛫Время {st} _по факту: {etad}\n'
                   f'🕒До {st}: {time_left}\n'
                   f'🛬Время {st} по факту: {atad}\n'
                   f'📅Задержка рейса: {remark}\n'
                   f'🏢Терминал: {gate}\n'
                   f'🛄Багажная лента: {carousel}')

            print(txt)
            send_telegram(txt)


def raspars_data_uraport(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    tables = soup.find_all('a', class_='table-flex__row table-flex__row--link align-center')
    for table in tables:
        # print(table)
        flightNumber = table.find('div', class_='table-flex__td table-flex__td--type2').text.strip()
        #print(flightNumber, type(flightNumber))

        if any(flightN in flightNumber for flightN in flightNs):
            # print(table)
            if 'arr' in url:
                path_from = table.find('span', class_='table-flex__no-wrap').text.split()
                path_from = ' '.join(path_from)
                path_to = 'Уральск URA'

            else:
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

            if not any(date in [today, tomorrow] for date in dates):
                print("continue")
                continue

            txt = (f'🌐Аэропорт URA\n'
                   f'🛫Вылет из {path_from} в {path_to}\n'
                   f'✈️Рейс: {flightNumber}\n'
                   f'💺Время вылета _по расп.: {stad}\n'
                   f'🛫Время вылета _по факту: {etad}\n'
                   f'🕒До вылета: {time_left}\n'
                   f'🛬Время прилета по факту: {atad}\n'
                   f'📅Задержка рейса: {remark}\n'
                   f'🏢Терминал: {gate}\n'
                   f'🛄Багажная лента: {carousel}')

            print(txt)
            send_telegram(txt)

def raspars_data_ya(url):
    pattern = r'fromName=(.*?)&toId='
    path_from = decode_string(extract_data(pattern, url))

    pattern = r'toName=(.*?)&when='
    path_to = decode_string(extract_data(pattern, url))

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Cache-Control": "max-age=0",
        "TE": "trailers"
    }

    response = requests.get(url, headers=headers)
    print(response)
    soup = BeautifulSoup(response.text, 'html.parser')
    print(soup)

    blocks = soup.find('tbody', class_='SearchSegments__tbody')
    blocks_tr = blocks.find_all('tr')
    for block in blocks_tr:
        print(block)

    print(path_from, path_to)
    input()

    txt = (f'Аэропорт YA\n'
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

def raspars_data_aerokz(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Cache-Control": "max-age=0",
        "TE": "trailers"
    }

    response = requests.get(url, headers=headers)
    #soup = BeautifulSoup(response.text, 'html.parser')

    detected_encoding = chardet.detect(response.content)['encoding']
    content = response.content.decode(detected_encoding)

    # Парсинг данных с BeautifulSoup
    soup = BeautifulSoup(content, 'html.parser')

    trs = soup.find_all('tr')

    if 'ALA' in url:
        city = 'Алматы ALA'

    elif 'URA' in url:
        city = 'Уральск URA'

    for tr in trs:
        columns = [td.text.strip() for td in tr.find_all('td')]
        #print(columns)

        if 'Вылет в' in columns:
            status = 'Вылет в'

        elif 'Прилет из' in columns:
            status = 'Прилет из'

        if any(flightN in str(columns) for flightN in flightNs):
            print('2', columns)

            if status == 'Вылет в':
                from_to = f"{status} {columns[0]} из {city}"

            elif status == 'Прилет из':
                from_to = f"{status} {city} в {columns[0]}"

            flightNumber = columns[1]
            stad = columns[2]
            etad = columns[3]
            if etad == '':
                etad = stad

            time_left = time_until(etad, timezone_str='Asia/Almaty')
            remark = columns[4]

            atad = ''
            gate = ''
            carousel = ''

            txt = (f'Аэропорт AIRO.KZ\n'
                   f'{from_to}\n'
                   f'Рейс: {flightNumber}\n'
                   f'Время вылета _по расп.: {stad}\n'
                   f'Время вылета _по факту: {etad}\n'
                   f'До вылета: {time_left}\n'
                   f'Время прилета по факту: {atad}\n'
                   f'Задержка рейса: {remark}\n'
                   f'Терминал: {gate}\n'
                   f'Багажная лента: {carousel}')

            print(txt)

    print('OK!')


def alaport():
    print('\nТабло ALA: Вылет из Уральска в Алматы')
    date = '2024-07-12'
    destination = 'ОРАЛ'
    airline = "FLY ARYSTAN"
    url = f'https://alaport.com/Home/searchFlights?flightLeg=ARR&date={date}&destination={destination}&airline={airline}&requestRawUrl=%2Fru-RU%2Fflights-ru%2Farrival-flights-ru'
    raspars_data_alaport(url)

    print('\nТабло ALA: Вылет из Алматы в Дубай')
    date = '2024-07-13'
    destination = 'ДУБАЙ'
    airline = 'FLY DUBAI'
    url = f'https://alaport.com/Home/searchFlights?flightLeg=DEP&date={date}&destination={destination}&airline={airline}&requestRawUrl=%2Fru-RU%2Fpassenger-ru%2Fflights-ru%2Fdeparture-flights-ru'
    raspars_data_alaport(url)

    print('\nТабло ALA: Вылет из Дубая в Алматы')
    date = '2024-07-23'
    destination = 'ДУБАЙ'
    airline = "FLY DYBAI"
    url = f'https://alaport.com/Home/searchFlights?flightLeg=ARR&date={date}&destination={destination}&airline={airline}&requestRawUrl=%2Fru-RU%2Fflights-ru%2Farrival-flights-ru'
    url = 'https://alaport.com/Home/searchFlights?flightLeg=ARR&date=2024-07-23&destination=%D0%94%D0%A3%D0%91%D0%90%D0%99&airline=FLY%20DUBAI&requestRawUrl=%2Fru-RU%2Fflights-ru%2Farrival-flights-ru'
    raspars_data_alaport(url)

    print('\nТабло ALA: Вылет из Алматы в Уральск')
    date = '2024-07-23'
    destination = 'ОРАЛ'
    airline = "FLY ARYSTAN"
    url = f'https://alaport.com/Home/searchFlights?flightLeg=DEP&date={date}&destination={destination}&airline={airline}&requestRawUrl=%2Fru-RU%2Fflights-ru%2Fdeparture-flights-ru'
    url = 'https://alaport.com/Home/searchFlights?flightLeg=DEP&date=2024-07-23&destination=%D0%9E%D0%A0%D0%90%D0%9B&airline=FLY%20ARYSTAN&requestRawUrl=%2Fru-RU%2Fflights-ru%2Fdeparture-flights-ru'
    raspars_data_alaport(url)


def uraport():
    print('\nТабло URA: Вылет из Уральска в Алматы')
    urls = ['https://ura.aero/ru/board/', 'https://ura.aero/ru/board/?date=tomorrow']
    for url in urls:
        raspars_data_uraport(url)

    print('\nТабло URA: Вылет из Алматы в Уральск')
    urls = ['https://ura.aero/ru/board/?type=arr', 'https://ura.aero/ru/board/?type=arr&date=tomorrow']
    for url in urls:
        raspars_data_uraport(url)

def yaport():
    date_0 = '12+июля'
    date_1 = '13+июля'
    date_2 = '23+июля'

    ala = ['c22177', 'Алматы']
    dbx = ['c11499', 'Дубай']
    ura = ['c10305', 'Уральск']

    print('Из Уральска в Алматы 12.07')
    url = 'https://rasp.yandex.kz/search/plane/?fromId=c10305&fromName=%D0%A3%D1%80%D0%B0%D0%BB%D1%8C%D1%81%D0%BA&toId=c22177&toName=%D0%90%D0%BB%D0%BC%D0%B0%D1%82%D1%8B&when=12+%D0%B8%D1%8E%D0%BB%D1%8F'
    raspars_data_ya(url)

    print('Из Алматы в Дубай 13.07')
    url = 'https://rasp.yandex.kz/search/plane/?fromId=c22177&fromName=%D0%90%D0%BB%D0%BC%D0%B0%D1%82%D1%8B&toId=c11499&toName=%D0%94%D1%83%D0%B1%D0%B0%D0%B9&when=13+%D0%B8%D1%8E%D0%BB%D1%8F'
    raspars_data_ya(url)

    print('Из Дубай в Алматы 23.07')
    url = 'https://rasp.yandex.kz/search/plane/?fromId=c11499&fromName=%D0%94%D1%83%D0%B1%D0%B0%D0%B9&toId=c22177&toName=%D0%90%D0%BB%D0%BC%D0%B0%D1%82%D1%8B&when=23+%D0%B8%D1%8E%D0%BB%D1%8F'
    raspars_data_ya(url)

    print('Из Алматы в Уральска 23.07')
    url = 'https://rasp.yandex.kz/search/plane/?fromId=c22177&fromName=%D0%90%D0%BB%D0%BC%D0%B0%D1%82%D1%8B&toId=c10305&toName=%D0%A3%D1%80%D0%B0%D0%BB%D1%8C%D1%81%D0%BA&when=23+%D0%B8%D1%8E%D0%BB%D1%8F'
    raspars_data_ya(url)


    url = 'https://travel.yandex.ru/avia/flights/KC-7166/?lang=ru&when=2024-07-02&from=URA'


def aeroportkz():
    urls = ['https://aeroport.kz/tablo.php?code=ala', 'https://aeroport.kz/tablo.php?code=ura']

    urls = ['https://aeroport.kz/tablo_ajax.php?code=ALA', 'https://aeroport.kz/tablo_ajax.php?code=URA']

    for url in urls:
        raspars_data_aerokz(url)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    alaport()
    uraport()
    #aeroportkz()

    #yaport()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
