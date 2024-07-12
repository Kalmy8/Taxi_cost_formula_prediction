import os

import requests
from dotenv import load_dotenv


class WeatherParser:
    def __init__(self, weather_api_key: str, city: str, latitude: str, longitude: str):
        self.weather_api_key = weather_api_key
        self.city = city
        self.latitude = latitude
        self.longitude = longitude

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


def main():
    # WeatherParser required parameters
    load_dotenv()
    OPENWEATHER_API_KEY = str(os.getenv("OPENWEATHER_API_KEY"))
    CITY = str(os.getenv("CITY"))
    LATITUDE = str(os.getenv("LATITUDE"))
    LONGITUDE = str(os.getenv("LONGITUDE"))
    weather = WeatherParser(OPENWEATHER_API_KEY, CITY, LATITUDE, LONGITUDE)
    print(weather.get_weather_dict())


if __name__ == "__main__":
    main()
