import argparse
import csv
import os
import time
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from selenium import webdriver
from tqdm import tqdm

from taxi.data.mine_taxi_website import TaxiParser
from taxi.data.mine_weather import WeatherParser


# Function to check and load missing environment variables
def check_and_load_env_variables(required_env_variables):
    # Check for missing environment variables
    missing_args = [arg for arg in required_env_variables if os.getenv(arg, "") == ""]

    if missing_args:
        # Print missing variables
        for arg in missing_args:
            print(f"Environment variable {arg} is not set")

        # Load environment variables from .env file
        print("Loading environmental variables from .env file...")
        load_dotenv()

        # Check again for missing variables after loading .env file
        missing_args_after_load = [
            arg for arg in required_env_variables if os.getenv(arg) == ""
        ]

        if missing_args_after_load:
            # Print missing variables after attempting to load .env file
            for arg in missing_args_after_load:
                print(f"Environment variable {arg} is missing in .env file")

            print(
                "Please provide all required environmental variables and check the .env file"
            )
            raise ValueError("Missing required environmental variables")


def main():
    parser = argparse.ArgumentParser(
        description="Launch data mining script for taxi aggregator website."
    )

    # Adding arguments
    parser.add_argument(
        "frequency", type=int, help="Specify <N> minutes to collect new observation"
    )

    # Parsing arguments
    args = parser.parse_args()

    # Load all the environmental variables
    required_env_variables = [
        "ADDRESS_BASE_URL",
        "STORED_ADDRESSES_PATH",
        "CSV_DATABASE_PATH",
        "MS_EDGE_USER_DATA_PATH",
        "CITY",
        "LATITUDE",
        "LONGITUDE",
        "OPENWEATHER_API_KEY",
    ]

    check_and_load_env_variables(required_env_variables)
    CSV_FILE_path = Path(os.getenv("CSV_DATABASE_PATH", ""))
    USER_DATA_path = Path(os.getenv("MS_EDGE_USER_DATA_PATH", ""))

    # Split USER_DATA_path to user-data-dir and profile-directory, as required by selenium.options.add_argument(...) function
    USER_DATA_dir_str = str(USER_DATA_path.parent)
    USER_DATA_profile_str = str(USER_DATA_path.name)

    # Ensure the data directory exists
    os.makedirs(CSV_FILE_path.parent, exist_ok=True)

    print("PARAMETERS INITIALIZED CORRECTLY...")

    # Setup Edge options
    options = webdriver.EdgeOptions()
    options.use_chromium = True
    options.add_argument("--headless")  # Run headless browser (without GUI)
    options.add_argument(f"--user-data-dir={USER_DATA_dir_str}")
    options.add_argument(f"--profile-directory={USER_DATA_profile_str}")
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
            with open(CSV_FILE_path, mode="a", newline="", encoding="utf-8") as file:
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
