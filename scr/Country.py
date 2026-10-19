import requests

from translate import Translator
from countryinfo import CountryInfo


class Country:
    LANGIUAGE_DICT = ""
    DRIVE_DICT = {"left": "левостороннее", "right": "правостороннеe"}
    to_rus = Translator(from_lang="en", to_lang="ru")

    def __init__(self, data):
        self.name = data[0]
        self.code = data[1]
        self.lat = data[2]
        self.lng = data[3]
        self.currency = data[4]
        self.drive_info = data[5]
        self.continent = data[6]
        self.flag = self.get_flag()
        self.base_curr_list, self.target_curr_list = self.get_curr_lists()
        self.get_lang()
        self.currency["ru_name"] = self.to_rus.translate(self.currency["name"])
        self.region = self.to_rus.translate(self.continent)

    def get_flag(self):
        flag_url = f"https://flagcdn.com/160x120/{self.code}.png"
        flag = requests.get(flag_url).content
        out = open("resources/flag.png", "wb")
        out.write(flag)
        out.close()
        return flag

    def get_curr_lists(self):
        popular = ["RUB", "USD", "EUR"]
        local = self.currency["code"]
        if local in popular:
            popular.remove(local)
        base_list = popular.copy()
        base_list.insert(0, local)
        target_list = popular + [local]
        return base_list, target_list

    def get_country_info(self):
        to_eng = Translator(from_lang="ru", to_lang="en")
        name_eng = to_eng.translate(self.name)
        country = CountryInfo(name_eng)
        capital = self.to_rus.translate(country.capital())
        languages = country.languages()
        population = round(country.population() / 1000000, 2)
        wiki = "https://ru.wikipedia.org/wiki/" + self.name
        currency_name = self.currency["ru_name"]
        drive = self.DRIVE_DICT[self.drive_info]
        text = (f"{self.name} находится в регионе {self.region},\nстолица - город {capital},"
                f"\nнаселение - {population} миллионов человек,\nвалюта - {currency_name},\nдвижение {drive},\n")
        lang_names = []
        for lang in languages:
            if self.LANGIUAGE_DICT[lang] == "German":
                lang_names.append("немецкий язык")
            else:
                name = self.LANGIUAGE_DICT[lang] + " language"
                lang_names.append(self.to_rus.translate(name).lower())
        if len(languages) == 1:
            text += f"официальный язык - {lang_names[0]}"
        else:
            all_lang = ", ".join(lang_names)
            text += f"официальные языки:  {all_lang}"
        text += f"\nбольше информации доступно на сайте "
        link = f'<a href={wiki}>Википедии</a><br>'
        return text, link

    # создаем словарь всех языков и их кодов, если он еще не был создан
    def get_lang(self):
        if Country.LANGIUAGE_DICT == "":
            with open('resources/languages.txt', 'r') as file:
                data = file.readlines()
                res = {}
                for line in data:
                    splitted = line.strip().split()
                    res[splitted[0]] = splitted[1]
            Country.LANGIUAGE_DICT = res
