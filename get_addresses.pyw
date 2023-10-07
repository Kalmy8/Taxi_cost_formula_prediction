from requests import Session
from bs4 import BeautifulSoup
import pickle
from random import shuffle
import os
clear = lambda: os.system('cls')
import clipboard

base_url = "https://dom.mingkh.ru/sverdlovskaya-oblast/ekaterinburg/houses"
headers = {
    "user-agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36 Edg/111.0.1661.54"
}

def collect_adresses(base_url):
    s = Session()
    s.headers.update(headers)

    Adresses = []
    i = 1
    while True:
        print(f"Getting  {i}/ ~ 90")
        response = s.get(base_url + f"?page={i}")
        i += 1

        soup = BeautifulSoup(response.text, "html.parser")
        address_modified = 0
        for _td in soup.find_all("td"):
            if _td.find("a"):
                Adresses.append(_td.find("a").text)
                address_modified = True

        if not address_modified:
            return Adresses


def get_random_address():
    try:
        with open("stored_address.pickle", 'rb') as file:
            Adresses = pickle.load(file)

    except Exception as err:
        print("File not found, collecting data...")
        Adresses = collect_adresses(base_url)

        with open("stored_address.pickle", 'wb') as file:
            pickle.dump(Adresses, file)

    shuffle(Adresses)

    try:
        with open('transfer_file.txt', 'a') as f:
            f.write('Екатеринбург,' + Adresses[0] + '\n')
    except Exception:
        print("Txt transfer file is missing!")
        exit(0)

    clipboard.copy(Adresses[0])

if __name__ == '__main__':
    get_random_address()