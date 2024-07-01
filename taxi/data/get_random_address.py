import requests
from bs4 import BeautifulSoup
from random import shuffle
import clipboard
from dotenv import load_dotenv
import os
from pathlib import Path

# Load environment variables from .env file
load_dotenv()

# Access variables using os.environ
ADDRESS_BASE_URL = os.environ.get("ADDRESS_BASE_URL")

DATA_DIR = Path(os.environ.get("DATA_DIR"))
STORED_ADDRESSES = Path(os.environ.get("STORED_ADDRESSES"))

STORED_ADDRESSES_PATH = DATA_DIR / STORED_ADDRESSES

HEADERS = {
    'user-agent' : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36 Edg/111.0.1661.54",
    'Accept-Language': 'en,en-GB;q=0.9,en-US;q=0.8,ru;q=0.7',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Referer': 'https://www.google.com/',
    'DNT': '1',  # Do Not Track Request Header
    'Upgrade-Insecure-Requests': '1'
}



def collect_addresses(base_url: str) -> list[str]:
    """
    Fetches house addresses from the provided URL, expecting them to be organized in html table.

    :param base_url: URL of a webpage containing city addresses.
    :return: list of addresses.
    """
    session = requests.Session()
    session.headers.update(HEADERS)

    addresses = []
    page_number = 1

    while True:
        print(f"Getting {page_number}/ ~ 90")
        response = session.get(base_url + f"?page={page_number}", cookies={'from-my': 'browser'})
        page_number += 1

        soup = BeautifulSoup(response.text, "html.parser")
        addresses_found = False

        for td in soup.find_all("td"):
            if link := td.find("a"):
                addresses.append(link.text)
                addresses_found = True

        if not addresses_found:
            break

    return addresses

def get_random_address() -> str:
    '''
    Tries to read one random address from STORED_ADDRESSES_PATH, else collects addresses using internet.
    :return: one single address presented as str
    '''
    try:
        with open(STORED_ADDRESSES_PATH, 'r') as file:
            addresses = file.read().splitlines()
            if len(addresses) == 0:
                raise EOFError

    except (FileNotFoundError, EOFError):
        print("File not found, collecting data...")
        addresses = collect_addresses(ADDRESS_BASE_URL)
        with open(STORED_ADDRESSES_PATH, 'w') as file:
            for address in addresses:
                file.write(f"{address}\n")

    shuffle(addresses)
    return addresses[0]

if __name__ == '__main__':
    get_random_address()
