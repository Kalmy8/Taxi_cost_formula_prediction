import json
import os

import requests
from dotenv import load_dotenv


class WeatherParser:
    def __init__(self):
        load_dotenv()
        self.weather_api_key = os.getenv("OPENWEATHER_API_KEY")

        # Load config.json file
        with open("config.json", "r") as config_file:
            config = json.load(config_file)

        # Access location parameters from config.json
        self.city = config["city"]
        self.latitude = config["latitude"]
        self.longitude = config["longitude"]

    def get_weather_dict(self) -> dict[str, str]:
        """
        Use https://api.openweathermap.org and given latitude, longitude, to define local weather parameters.
        :return: Actual weather state, temperature (celsius) and humidity (%)
        """
        try:
            res = requests.get(
                "https://api.openweathermap.org/data/2.5/weather",
                params={
                    "lat": self.latitude,
                    "lon": self.longitude,
                    "units": "metric",
                    "appid": self.weather_api_key,
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
            return {"Actual_state": "", "Temp": "", "Humidity": ""}


if __name__ == "__main__":
    weather = WeatherParser()
    print(weather.get_weather_dict())
