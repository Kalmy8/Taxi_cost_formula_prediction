import argparse
import csv
import json
import os
import time
from datetime import datetime
from pathlib import Path

from selenium import webdriver
from tqdm import tqdm

from taxi.data.mine_taxi_website import TaxiParser
from taxi.data.mine_weather import WeatherParser


def main():
    parser = argparse.ArgumentParser(description="Data parser invokation frequency")

    # Adding arguments
    parser.add_argument(
        "frequency", type=int, help="Every <N> minutes collect new observation"
    )

    # Parsing arguments
    args = parser.parse_args()

    # Load config.json file
    with open("config.json", "r") as config_file:
        config = json.load(config_file)

    # Define paths for the CSV file
    CSV_FILE_path = Path(config["CSV_DATABASE_PATH"])

    # Ensure the data directory exists
    os.makedirs(CSV_FILE_path.parent, exist_ok=True)

    print("PARAMETERS INITIALIZED CORRECTLY...")

    # Setup Edge options
    options = webdriver.EdgeOptions()
    options.use_chromium = True
    options.add_argument("--headless")  # Run headless browser (without GUI)
    options.add_argument("--user-data-dir=C:\\User Data")
    options.add_argument("--profile-directory=Default")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    # Initialize the driver
    driver = webdriver.Edge(options=options)

    print("WEBDRIVER OPENED SUCCESSFULLY...")

    try:
        while True:
            data = {"timestamp": datetime.now().strftime("%Y-%m-%d %H:%M")}

            # Get predictors data
            taxi = TaxiParser(driver)
            taxi_dict = taxi.get_ride_info_dict()
            print("TAXI INFORMATION PARSED...")

            weather = WeatherParser()
            print("WEATHER INFORMATION PARSED...")

            weather_dict = weather.get_weather_dict()

            # Combine data
            data.update(taxi_dict)
            data.update(weather_dict)

            # Write to CSV
            file_exists = os.path.isfile(CSV_FILE_path)
            with open(CSV_FILE_path, mode="a", newline="") as file:
                writer = csv.DictWriter(file, fieldnames=data.keys())
                if not file_exists:
                    writer.writeheader()
                writer.writerow(data)

            total_time = 60 * args.frequency  # in seconds
            total_iterations = 100
            sleep_duration = total_time / total_iterations

            # Use tqdm to display a progress bar
            for i in tqdm(
                range(total_iterations),
                desc=f"SLEEPING, NEXT INVOKATION IN {total_time} SECONDS",
            ):
                time.sleep(sleep_duration)

    finally:
        driver.quit()


if __name__ == "__main__":
    main()
