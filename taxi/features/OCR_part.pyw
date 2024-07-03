import datetime
import glob
import json
import os
import re
from datetime import datetime

import numpy
import pandas as pd
import requests

dir_path = os.path.dirname(os.path.realpath(__file__))

# Добавляет в словарь информацию о текущей дате
def append_actual_time(base_dict: dict) -> dict:
    base_dict['Time'] = datetime.now().replace(second=0, microsecond=0)
    return base_dict

# Класс, достающий информацию о погоде и дистанции

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
    print("Data has been updated!")


if __name__ == '__main__':
    main()
