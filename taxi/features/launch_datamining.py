import argparse
import csv
import os
import subprocess
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
            arg for arg in required_env_variables if os.getenv(arg, "") == ""
        ]

        if missing_args_after_load:
            # Print missing variables after attempting to load .env file
            for arg in missing_args_after_load:
                print(f"Environment variable {arg} is missing in .env file")

            print(
                "Please provide all required environmental variables and check the .env file"
            )
            raise ValueError("Missing required environmental variables")


def git_setup():
    """
    Sets github globals to allow working with remote repository
    """
    GITHUB_USERNAME = os.getenv("GITHUB_USERNAME", "")
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
    GITHUB_EMAIL = os.getenv("GITHUB_EMAIL", "")
    REPO_URL = os.getenv("REPO_URL", "")

    # Strip original URL for use with GITHUB_TOKEN
    REPO_URL_STRIPPED = REPO_URL.removeprefix("https://")

    # Configure Git to use the PAT
    subprocess.run(["git", "config", "--global", "user.name", GITHUB_USERNAME], check=True)
    subprocess.run(["git", "config", "--global", "user.email", GITHUB_EMAIL], check=True)
    subprocess.run(
        ["git", "remote", "set-url", "origin", f"https://{GITHUB_TOKEN}@{REPO_URL_STRIPPED}"],
        check=True,
    )


def git_pull_remote_data():
    BRANCH_NAME = os.getenv("DATA_BRANCH_NAME", "")
    CSV_DATABASE_PATH = os.getenv("CSV_DATABASE_PATH", "")

    subprocess.run(["git", "fetch", "origin"], check=True)
    subprocess.run(
        ["git", "checkout", f"origin/{BRANCH_NAME}", "--", f"{CSV_DATABASE_PATH}"], check=True
    )


def git_push_mined_data():
    """
    Removes all files from git index, adds only data/data.csv file, commits and pushes it to the
    remote DATA_BRANCH repository, when resets branch to the latest commit

    """
    BRANCH_NAME = os.getenv("DATA_BRANCH_NAME", "")
    CSV_DATABASE_PATH = os.getenv("CSV_DATABASE_PATH", "")

    subprocess.run(["git", "rm", ".", "-r", "--cached", "-f", ">", "/dev/null"], check=True)
    subprocess.run(["git", "add", "-f", f"{CSV_DATABASE_PATH}"], check=True)
    subprocess.run(
        ["git", "commit", "-m", "Automated data push", "--no-verify"],
        check=True,
    )
    subprocess.run(["git", "push", "origin", f"HEAD:{BRANCH_NAME}", "-f"], check=True)
    subprocess.run(["git", "reset", "--hard", "HEAD~1"], check=True)

    print("Changes are successfully pushed")


def write_to_csv(CSV_FILE_path: Path, data: dict[str, str]):
    """
    Writes data to the end of specified .csv file
    :param CSV_FILE_path: points to the data-storage .csv file
    :param data: data to write
    """
    file_exists = os.path.isfile(CSV_FILE_path)
    with open(CSV_FILE_path, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=data.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(data)


def main():
    parser = argparse.ArgumentParser(
        description="Launch data mining script for taxi aggregator website. Requires environmental variables to run"
    )

    # Adding arguments
    parser.add_argument(
        "--mining_frequency", type=int, help="Specify <N> minutes to collect new observation"
    )

    # Adding arguments
    parser.add_argument(
        "--new_observations_per_push",
        type=int,
        default=None,
        help="Specify number of new mined observations to push them into git",
    )

    # Parsing arguments
    args = parser.parse_args()

    # Specify all the environmental variables
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

    # If runned via docker, host MSEDGE folder is mounted into /app/MSEDGE_USER_DATA folder
    DOCKER_ENV = os.getenv("DOCKER_ENV")
    if DOCKER_ENV:
        USER_DATA_path = Path("/app/MSEDGE_USER_DATA")
    else:
        USER_DATA_path = Path(os.getenv("MS_EDGE_USER_DATA_PATH", ""))

    # Split USER_DATA_path to user-data-dir and profile-directory, as required by selenium.options.add_argument(...) function
    USER_DATA_dir_str = str(USER_DATA_path.parent)
    USER_DATA_profile_str = str(USER_DATA_path.name)

    # TaxiParser required parameters
    ADDRESS_BASE_URL_str = os.getenv("ADDRESS_BASE_URL", "")
    STORED_ADDRESSES_path = Path(os.getenv("STORED_ADDRESSES_PATH", ""))

    # WeatherParser required parameters
    OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "")
    CITY = os.getenv("CITY", "")
    LATITUDE = os.getenv("LATITUDE", "")
    LONGITUDE = os.getenv("LONGITUDE", "")

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
        if args.new_observations_per_push:
            required_env_variables = [
                "GITHUB_USERNAME",
                "GITHUB_TOKEN",
                "GITHUB_EMAIL",
                "REPO_URL",
                "DATA_BRANCH_NAME",
            ]
            check_and_load_env_variables(required_env_variables)
            batch_observations = []
            i = 0
            git_setup()

        while True:
            data = {"timestamp": datetime.now().strftime("%Y-%m-%d %H:%M")}

            # Get predictors data
            taxi = TaxiParser(driver, STORED_ADDRESSES_path, ADDRESS_BASE_URL_str)
            taxi_dict = taxi.get_ride_info_dict()
            print("TAXI INFORMATION PARSED...")

            weather = WeatherParser(OPENWEATHER_API_KEY, CITY, LATITUDE, LONGITUDE)
            print("WEATHER INFORMATION PARSED...")

            weather_dict = weather.get_weather_dict()

            # Combine data
            data.update(taxi_dict)
            data.update(weather_dict)

            # Append data to the local storage
            if args.new_observations_per_push is None:
                write_to_csv(CSV_FILE_path, data)

            # Push N new-observations to git
            else:
                batch_observations.append(data)
                i += 1
                if i % args.new_observations_per_push == 0:
                    # Fetch actual remote data
                    git_pull_remote_data()

                    # Write all collected data batch to the remote database .csv file
                    for data in batch_observations:
                        write_to_csv(CSV_FILE_path, data)

                    # Push mined data to the remote DATA_BRANCH
                    git_push_mined_data()

                    # Empty copied differencies
                    batch_observations = []

            total_time = 60 * args.mining_frequency  # in seconds
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
