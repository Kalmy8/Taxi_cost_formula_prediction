import os
import time
from pathlib import Path

from selenium import webdriver
from selenium.common import NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from taxi.data.get_random_address import get_random_address


class TaxiParser:
    def __init__(
        self, driver: webdriver, STORED_ADDRESSES_path: Path, ADDRESS_BASE_URL_str: str
    ):
        self.driver = driver
        self.driver.implicitly_wait(5)
        self.STORED_ADDRESSES_path = STORED_ADDRESSES_path
        self.ADDRESS_BASE_URL_str = ADDRESS_BASE_URL_str

    def get_ride_info_dict(self) -> dict[str, str]:
        ride_info: dict[str, str] = dict()
        self.__open_website()
        self.__enter_keys_and_get_distance(ride_info)
        self.__get_prices(ride_info)
        self.__get_time(ride_info)

        return ride_info

    def __open_website(self):
        self.driver.get("https://taxi.yandex.ru/")

    def __enter_keys_and_get_distance(self, ride_info: dict[str, str]):
        # Wait for elements to be presented
        textareas = WebDriverWait(self.driver, 5).until(
            EC.presence_of_all_elements_located((By.TAG_NAME, "textarea"))
        )

        used_addresses = []
        for i in range(2):
            # Get corresponding textarea
            textarea = textareas[i]

            # Enters single address
            address = get_random_address(
                self.STORED_ADDRESSES_path, self.ADDRESS_BASE_URL_str
            )
            used_addresses.append(address)
            textarea.send_keys(Keys.CONTROL + "a")
            time.sleep(1)
            textarea.send_keys(Keys.DELETE)
            time.sleep(1)
            textarea.send_keys(address)
            time.sleep(2)

            # Catch floating window with valid addresses helper
            floating_addresses_div = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, "div.VerticalScroll--q4j8Q.vertical--xrlWR")
                )
            )
            first_child = floating_addresses_div.find_element(By.CSS_SELECTOR, ":first-child")

            # For second area, also capture displayed distance
            if i == 1:
                # Retry mechanism for floating window
                max_retries = 3
                for attempt in range(max_retries):
                    try:
                        distance_element = self.driver.find_element(
                            By.CSS_SELECTOR,
                            "div.result-distance--kYtjt.result-distance--FaJyS",
                        )

                        ride_info["Дистанция"] = distance_element.text
                        break

                    except (StaleElementReferenceException, NoSuchElementException):
                        if attempt < max_retries - 1:
                            time.sleep(3)  # wait before retrying
                        else:
                            raise  # re-raise the exception after the last attempt

            first_child.click()
            time.sleep(3)

        ride_info["Точка отправления"] = used_addresses[0]
        ride_info["Точка прибытия"] = used_addresses[1]

    def __get_prices(self, ride_info: dict[str, str]):
        # Find all elements with class "priceText"
        taxi_classes = self.driver.find_elements(By.CSS_SELECTOR, "span.title--rOp0c")
        prices = self.driver.find_elements(By.CSS_SELECTOR, "span.priceText--oa4eD")

        for taxi_class, price in zip(taxi_classes, prices):
            only_digits = "".join(filter(str.isdigit, price.text))
            ride_info[f"{taxi_class.text}"] = only_digits

    def __get_time(self, ride_info: dict[str, str]):
        span_hints = self.driver.find_elements(By.CSS_SELECTOR, "span.hint--AH9wx")
        ride_info["Длительность"] = span_hints[1].text[7:]


def main():
    # Setup Edge options
    options = webdriver.EdgeOptions()

    options.use_chromium = True
    # options.add_argument("--headless")  # Run headless browser (without GUI)
    options.add_argument("--user-data-dir=C:\\User Data")
    options.add_argument("--profile-directory=Default")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    # Initialize the driver
    driver = webdriver.Edge(options=options)
    driver.implicitly_wait(5)

    # Load environment variables
    ADDRESS_BASE_URL_str = os.getenv("ADDRESS_BASE_URL", "")
    STORED_ADDRESSES_path = Path(os.getenv("STORED_ADDRESSES_PATH", ""))

    taxi = TaxiParser(driver, STORED_ADDRESSES_path, ADDRESS_BASE_URL_str)
    ride_info = taxi.get_ride_info_dict()
    print(ride_info)


if __name__ == "__main__":
    main()
