"""
This module gets the last screenshot in /screenshots directory and extracts info
"""
import datetime
import glob
import json
import os
import re
from datetime import datetime

import easyocr
import numpy
import pandas as pd
import requests
from PIL import Image

dir_path = os.path.dirname(os.path.realpath(__file__))

# Добавляет в словарь информацию о текущей дате
def append_actual_time(base_dict: dict) -> dict:
    base_dict['Time'] = datetime.now().replace(second=0, microsecond=0)
    return base_dict

# Находит в спец. директории последний из скриншотов
def get_latest_screenshot() -> numpy.array:
    list_of_files = glob.glob(f'{dir_path}/screenshots/*')
    latest_file = max(list_of_files, key=os.path.getctime)
    return latest_file

# Распознавалка, возвращает список с текстом
def digit_recognition(screenshot_path: str) -> list:
    im = Image.open(screenshot_path)
    pix = numpy.array(im)
    reader = easyocr.Reader(['ru'], gpu= False)
    bounds = reader.readtext(pix, allowlist = 'Ккуда?₽мМиИнН0123456789', detail=0)
    return bounds

# Класс, достающий информацию о погоде и дистанции

class Web_scraper:

    # Используя openweathermap API, достает информацию о погоде
    @staticmethod
    def get_weather() -> dict:
        appid = "a807e0ddb2aaf30042955bc4b0fc15ba"
        lat, lon = [56.8575, 60.6125]

        try:
            res = requests.get("https://api.openweathermap.org/data/2.5/weather",
                               params={'lat': lat, 'lon': lon, 'units': 'metric', 'appid': appid})
            data = res.json()
            print(data)

            return {'Actual_state' :  data['weather'][0]['description'],
                    'Temp' : str(data['main']['temp']) + "C",
                    'Humidity' : str(data['main']['humidity']) + "%"}

        except Exception as e:
            print("Exception (weather):", e)
            return {'Actual_state': None,
                    'Temp': None,
                    'Humidity': None}

    # Используя Геокодер яндекса и api OSMR project, находит расстояние между двумя адресами в Екатеринбурге
    @staticmethod
    def get_distance() -> dict:
        # call the OSMR API
        api_key = 'bb9bd3e2-baa6-4edd-9f31-4f946c7d63f4'

        try:
            with open(f'{dir_path}/transfer_file.txt', 'r+') as f:
                adr1, adr2 = f.read().splitlines()

        except Exception as err:
            print(err)
            exit(1)

        r1 = requests.get(f"https://geocode-maps.yandex.ru/1.x?format=json&apikey={api_key}&geocode={adr1}")
        r2 = requests.get(f"https://geocode-maps.yandex.ru/1.x?format=json&apikey={api_key}&geocode={adr2}")


        lon_1, lat_1 = r1.json()['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['Point']['pos'].split()
        lon_2, lat_2 = r2.json()['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['Point']['pos'].split()

        r = requests.get(f"http://router.project-osrm.org/route/v1/car/{lon_1},{lat_1};{lon_2},{lat_2}?overview=false""")
        # then you load the response using the json libray
        # by default you get only one alternative so you access 0-th element of the routes
        routes = json.loads(r.content)
        route_1 = routes.get("routes")[0]
        return {"Distance" : route_1['legs'][0]['distance']}

# Формирует список цен и длительность поездки
class Filter:

    # Первичная фильтрация, выбирает из всех блоков те, в которых содержится стоимость
    def __filtering_mask(input_list):
        digital_positions = [2,8,9,10,13,14]
        return [input_list[ix] for ix in digital_positions]

    # Выделаяет числа
    def __extract_decimals(input_string):
        return int(*re.findall("\d+", input_string, re.IGNORECASE))

    # Удаляет символ повышенного спроса
    def __sharp_deleter(filtered_bounds : list) -> list:
        business_price = filtered_bounds[-2]
        for ix, price in enumerate(filtered_bounds):
            if price > business_price:
                filtered_bounds[ix] = int(str(price)[1:]) # Превращаем число в строку и удаляем 1й символ

        return filtered_bounds

    # Осуществляет всю фильтрацию
    @staticmethod
    def filter_text(bounds: list) -> dict:
        taxi_types = ['Economy', 'Comfort', 'Comfort+', 'Business', 'Kids']
        base_dict = dict()

        first_cut = Filter.__filtering_mask(bounds)
        decimals_list = [Filter.__extract_decimals(str) for str in first_cut if Filter.__extract_decimals(str) != 0]
        values = Filter.__sharp_deleter(decimals_list)

        base_dict['Duration'] = values[0]
        base_dict['Taxi_type'] = taxi_types
        base_dict['Price'] = values[1:]

        return base_dict

# Открывает pickle DF и заносит в него новую строчку
class Form_DF:

    # Открывает DF под именем 'data.pkl' из рабочей директории, иначе создает новый
    @staticmethod
    def open_DF():
        try:
            df = pd.read_pickle(f'{dir_path}/data.pkl')
            print("Pickle database found, opening...")

        except Exception as e:
            print("Pickle database not found, creating new one...")
            df = pd.DataFrame(
                columns=['Time', 'Duration', 'Distance', 'Actual_state','Temp','Humidity','Taxi_type','Price'])

        return df

    # Из словаря делает несколько новых строк
    @staticmethod
    def __form_new_row(info : dict) -> pd.DataFrame:
        new_row = pd.DataFrame(info)
        new_row = new_row.explode(['Taxi_type', 'Price'])
        return  new_row

    # Добавляет строки в DF, обновляет pkl файл.
    @staticmethod
    def insert_info(info : dict):
        df = Form_DF.open_DF()
        new_piece = Form_DF.__form_new_row(info)
        df = pd.concat([df, new_piece])
        df = df.drop_duplicates() # На случай, если новый скриншот не возник
        pd.to_pickle(df, f'{dir_path}/data.pkl')


def main():
    screen = get_latest_screenshot()
    bounds = digit_recognition(screen)  # Распознаем текст со скриншота
    pricelist = Filter.filter_text(bounds)  # Достаем всю информацию о ценах
    pricelist = append_actual_time(pricelist) # Добавляем дату
    pricelist.update(Web_scraper.get_weather()) # Добавляем погоду
    pricelist.update(Web_scraper.get_distance()) # И добавляем дистанцию между точками
    Form_DF.insert_info(pricelist) # Открывает базу данных, добавляет новую запись
    print("Data has been updated!")


if __name__ == '__main__':
    main()
    #print(Form_DF.open_DF().info())