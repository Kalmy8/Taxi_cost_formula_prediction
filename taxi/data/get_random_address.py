import os
from pathlib import Path
from random import shuffle

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv


def collect_addresses(base_url: str) -> list[str]:
    """
    Fetches house addresses from the provided URL,
    expecting them to be organized in html table.
    :param base_url: URL of a webpage containing city addresses.
    :return: list of addresses.
    """

    HEADERS = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) \
                       AppleWebKit/537.36 (KHTML, like Gecko) \
                       Chrome/111.0.0.0 \
                       Safari/537.36 Edg/111.0.1661.54",
        "Accept-Language": "en,en-GB;q=0.9,en-US;q=0.8,ru;q=0.7",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Referer": "https://www.google.com/",
        "DNT": "1",  # Do Not Track Request Header
        "Upgrade-Insecure-Requests": "1",
    }

    session = requests.Session()
    session.headers.update(HEADERS)

    addresses = []
    page_number = 1

    while True:
        print(f"Getting {page_number}/ ~ 90")
        response = session.get(
            base_url + f"?page={page_number}", cookies={"from-my": "browser"}
        )
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


def get_random_address(STORED_ADDRESSES_path: Path, ADDRESS_BASE_URL_str: str) -> str:
    """
    Tries to read one random address from STORED_ADDRESSES_PATH,
    else collects addresses using internet.
    :param STORED_ADDRESSES_path: Path to the file containing city addresses.
    :param ADDRESS_BASE_URL_str: Web-address to parse city addresses from
    :return: one single address presented as str
    """

    try:
        with open(STORED_ADDRESSES_path, "r", encoding="utf8") as file:
            addresses = file.read().splitlines()
            if len(addresses) == 0:
                raise EOFError

    except (FileNotFoundError, EOFError):
        print("File not found, collecting data...")
        addresses = collect_addresses(ADDRESS_BASE_URL_str)
        with open(STORED_ADDRESSES_path, "w", encoding="utf8") as file:
            for address in addresses:
                file.write(f"{address}\n")

    shuffle(addresses)
    return addresses[0]


def main():
    # Load environment variables
    load_dotenv()
    ADDRESS_BASE_URL_str = str(os.getenv("ADDRESS_BASE_URL"))
    STORED_ADDRESSES_path = Path(str(os.getenv("STORED_ADDRESSES_PATH")))

    get_random_address(STORED_ADDRESSES_path, ADDRESS_BASE_URL_str)


if __name__ == "__main__":
    main()
