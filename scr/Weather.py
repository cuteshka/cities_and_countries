import requests
import requests_cache
from retry_requests import retry
import openmeteo_requests


class Weather:
    URL = "https://api.open-meteo.com/v1/forecast"
    # код со страницы https://open-meteo.com/en/docs#current=&wind_speed_unit=ms
    cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
    retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
    openmeteo = openmeteo_requests.Client(session=retry_session)

    # погода сейчас
    @staticmethod
    def get_current_weather(lat, lng):
        params = {
            "latitude": lat,
            "longitude": lng,
            "current": ["temperature_2m", "relative_humidity_2m", "precipitation", "cloud_cover", "surface_pressure",
                        "wind_speed_10m"]
        }
        responses = Weather.openmeteo.weather_api(Weather.URL, params=params)
        current = responses[0].Current()
        temperature = int(current.Variables(0).Value())
        humidity = int((current.Variables(1).Value()))
        precipitation = current.Variables(2).Value()
        cloud = int(current.Variables(3).Value())
        pressure = int(current.Variables(4).Value() / 1.333)
        wind = round(current.Variables(5).Value() * 1000 / 3600, 1)
        text = (f"Сейчас в городе температура воздуха {temperature}°C,\nосадки - {precipitation} мм,\nотносительная "
                f"влажность {humidity}%,\nоблачность {cloud}%,\nскорость ветра {wind} метров в секунду,\nатмосферное "
                f"давление {pressure} мм ртутного столба.")
        return text

    # прогноз
    @staticmethod
    def get_one_day_forecast(lat, lng, timezone):
        URL = (f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lng}&hourly=temperature_2m,"
               f"precipitation_probability,cloud_cover,wind_speed_10m&timezone={timezone}&forecast_days=2")
        answer = requests.get(
            URL)
        answer.raise_for_status()
        weather_json = answer.json()['hourly']
        time = weather_json["time"]
        temperature = weather_json['temperature_2m']
        precipitation = weather_json['precipitation_probability']
        cloud = weather_json['cloud_cover']
        wind = weather_json['wind_speed_10m']
        formatted_time = []
        for i in range(0, 24, 2):
            formatted_time.append(f"{i}ч")
        tomorrow_text = (
            f"Прогноз погоды на завтра, {time[-1][:10]}, отражена в таблице.\nДинамика температуры воздуха по часам "
            f"также отражена на диаграмме.")
        today_text = (
            f"Погода на сегодня {time[0][:10]} представлена в таблице.\nДинамика температуры воздуха по часам также "
            f"отражена на диаграмме.")
        today_temp = []
        tomorrow_temp = []
        other_info_today = []
        other_info_tomorrow = []
        for i in range(0, 48, 2):
            if i < 24:
                today_temp.append(int(temperature[i]))
                other_info_today.append((int(temperature[i]), precipitation[i], cloud[i], int(wind[i])))
            else:
                tomorrow_temp.append(int(temperature[i]))
                other_info_tomorrow.append((int(temperature[i]), precipitation[i], cloud[i], int(wind[i])))
        res_for_today = (today_text, formatted_time, today_temp, other_info_today)
        res_for_tomorrow = (tomorrow_text, formatted_time, tomorrow_temp, other_info_tomorrow)
        return res_for_today, res_for_tomorrow
