# This is a sample Python script.
import requests


# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

def ura_to_ala():
    date = '2024-06-29'
    url = f'https://alaport.com/Home/searchFlights?flightLeg=ARR&date={date}&destination=%D0%9E%D0%A0%D0%90%D0%9B&airline=FLY%20ARYSTAN&requestRawUrl=%2Fru-RU%2Fflights-ru%2Farrival-flights-ru'

    r = requests.get(url)
    print(r)



# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    ura_to_ala()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
