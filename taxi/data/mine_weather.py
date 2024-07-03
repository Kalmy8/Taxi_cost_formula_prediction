import json
import os
from typing import Optional

import requests
from dotenv import load_dotenv

load_dotenv()

weather_api_key = os.getenv("OPENWEATHER_API_KEY")

# Load config.json file
with open("config.json", "r") as config_file:
    config = json.load(config_file)

# Access location parameters from config.json
city = config["city"]
latitude = config["latitude"]
longitude = config["longitude"]


def get_weather(latitude, longitude, weather_api_key) -> dict[str, Optional[str]]:
    """
    Use https://api.openweathermap.org and given latitude, longitude, to define local weather parameters.
    :param latitude: Latitude of the interest location
    :param longitude: Longitude of the interest location
    :param weather_api_key: api-key, which must be got on the official <openweathermap> website
    :return: Actual weather state, temperature (celsius) and humidity (%)
    """
    try:
        res = requests.get(
            "https://api.openweathermap.org/data/2.5/weather",
            params={
                "lat": latitude,
                "lon": longitude,
                "units": "metric",
                "appid": weather_api_key,
            },
        )
        data = res.json()

        return {
            "Actual_state": data["weather"][0]["description"],
            "Temp": str(data["main"]["temp"]) + "C",
            "Humidity": str(data["main"]["humidity"]) + "%",
        }

    except Exception as e:
        print("Exception (weather):", e)
        return {"Actual_state": None, "Temp": None, "Humidity": None}


if __name__ == "__main__":
    get_weather(latitude, longitude, weather_api_key)
