import time
from collections import defaultdict

import pandas as pd
from get_random_address import get_random_address
from selenium import webdriver
from selenium.common import NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def open_driver() -> webdriver:
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

    # Open a website
    driver.get("https://taxi.yandex.ru/")
    return driver


def enter_keys_and_get_distance(
    driver: webdriver, ride_info: dict[str, list[list[str] | str]]
):
    # Wait for elements to be presented
    textareas = WebDriverWait(driver, 5).until(
        EC.presence_of_all_elements_located((By.TAG_NAME, "textarea"))
    )

    used_addresses = []
    for i in range(2):
        # Get corresponding textarea
        textarea = textareas[i]

        # Enters single address
        address = get_random_address()
        used_addresses.append(address)
        textarea.send_keys(Keys.CONTROL + "a")
        time.sleep(1)
        textarea.send_keys(Keys.DELETE)
        time.sleep(1)
        textarea.send_keys(address)
        time.sleep(2)

        # Catch floating window with valid addresses helper
        floating_addresses_div = WebDriverWait(driver, 5).until(
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
                    distance_element = driver.find_element(
                        By.CSS_SELECTOR, "div.result-distance--kYtjt.result-distance--FaJyS"
                    )

                    ride_info["Дистанция"].append(distance_element.text)
                    break

                except (StaleElementReferenceException, NoSuchElementException):
                    if attempt < max_retries - 1:
                        time.sleep(3)  # wait before retrying
                    else:
                        raise  # re-raise the exception after the last attempt

        first_child.click()
        time.sleep(3)

    ride_info["Адреса"].append(used_addresses)


def get_prices(driver: webdriver, ride_info: dict[str, list[list[str] | str]]):
    # Find all elements with class "priceText"
    taxi_classes = driver.find_elements(By.CSS_SELECTOR, "span.title--rOp0c")
    prices = driver.find_elements(By.CSS_SELECTOR, "span.priceText--oa4eD")

    for taxi_class, price in zip(taxi_classes, prices):
        ride_info[f"{taxi_class.text}"].append(price.text)


def get_time(driver: webdriver, ride_info: dict[str, list[list[str] | str]]):
    span_hints = driver.find_elements(By.CSS_SELECTOR, "span.hint--AH9wx")
    ride_info["Время"].append(span_hints[1].text[7:])


def main(loop_count: int) -> dict[str, list[list[str] | str]]:
    driver = open_driver()
    ride_info: dict[str, list[list[str] | str]] = defaultdict(lambda: [])
    for i in range(loop_count):
        enter_keys_and_get_distance(driver, ride_info)
        get_prices(driver, ride_info)
        get_time(driver, ride_info)

    driver.quit()
    return ride_info


if __name__ == "__main__":
    rides = main(3)
    print(pd.DataFrame(rides))
