import csv
from opencage.geocoder import OpenCageGeocode


class PlaceSearch:
    GEOKEY = OpenCageGeocode("53532ba5f03b48b0b9d3c633e44d97d4")

    # ищем страну
    @staticmethod
    def find_country(country):
        data = PlaceSearch.GEOKEY.geocode(country, language="ru")
        # если нашли страну, собираем информацию и возвращаем ее
        if data:
            lat = data[0]["geometry"]["lat"]
            lng = data[0]["geometry"]["lng"]
            currency_code = ""
            if "iso_code" in data[0]["annotations"]["currency"]:
                currency_code = data[0]["annotations"]["currency"]["iso_code"]
            currency_name = ""
            if "name" in data[0]["annotations"]["currency"]:
                currency_name = data[0]["annotations"]["currency"]["name"]
            currency_symbol = ""
            if "symbol" in data[0]["annotations"]["currency"]:
                currency_symbol = data[0]["annotations"]["currency"]["symbol"]
            currency = {"code": currency_code, "name": currency_name,
                        "symbol": currency_symbol}
            drive_info = ""
            if 'roadinfo' in data[0]["annotations"] and 'drive_on' in data[0]["annotations"]['roadinfo']:
                drive_info = data[0]["annotations"]['roadinfo']['drive_on']
            continent = data[0]["components"]['continent']
            country_code = data[0]["components"]["country_code"]
            return country, country_code, lat, lng, currency, drive_info, continent
        else:
            return []

    # ищем по стране и городу
    @staticmethod
    def find_city_in_country(city, country, country_code):
        # получаем список стран, в котором есть нужный город
        data = PlaceSearch.GEOKEY.geocode(city, language="ru")
        ind = None
        # проверяем, есть ли в списке нужная страна, если да, то сохраняем ее индекс
        if data:
            for i in range(len(data)):
                if data[i]["components"]["country_code"] == country_code:
                    ind = i
                    break
        # если нет, возвращаем пустой список
        if ind is None:
            return []
        # если страна найдена, находим и возвращаем данные о нужном городе
        else:
            lat = data[i]["geometry"]["lat"]
            lng = data[i]["geometry"]["lng"]
            region = ""
            if "region" in data[i]["components"]:
                region = data[i]["components"]["region"]
            state = ""
            if "state" in data[i]["components"]:
                state = data[i]["components"]["state"]
            timezone = {"name": data[i]["annotations"]["timezone"]["name"],
                        "offset": data[i]["annotations"]["timezone"]["offset_string"],
                        "code": data[i]["annotations"]["timezone"]["short_name"]}
            return city, lat, lng, region, state, timezone, country

    # создаем список стран в которых есть определенный город
    @staticmethod
    def find_countries_by_city(city):
        # находим все города с выбрвнным названием
        data = PlaceSearch.GEOKEY.geocode(city, language="ru")
        # создвем и возвращаем список стран, в которых есть этот город
        country_set = set()
        for i in range(len(data)):
            country_set.add(data[i]["components"]["country"])
        return list(country_set)

    # создаем словарь всех стран и их кодов
    @staticmethod
    def get_country_list():
        res = {}
        with open('resources/country.csv', encoding="utf8") as csvfile:
            data = csv.reader(csvfile, delimiter=',', quotechar='"')
            for index, line in enumerate(data):
                name = line[1]
                code = line[0].lower()
                if index > 1:
                    res[name] = code
        return res
