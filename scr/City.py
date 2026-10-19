import pytz
from datetime import datetime
from translate import Translator


class City:
    to_rus = Translator(from_lang="en", to_lang="ru")

    def __init__(self, data):
        self.name = data[0]
        self.lat = data[1]
        self.lng = data[2]
        self.region = data[3]
        self.state = data[4]
        self.timezone = data[5]
        self.country = data[6]
        self.timezone_pytz = ""

    # возвращает данные о часовом поясе в текстовом формате
    def get_time_info(self):
        here = datetime.now()
        tz_name = self.timezone["name"]
        tz_offset = self.timezone["offset"]
        tz_code = self.timezone["code"]
        self.timezone_pytz = pytz.timezone(tz_name)
        local = datetime.now(self.timezone_pytz)
        dif = local.hour - here.hour
        text = (f"Часовой пояс в городе {self.name} - {self.to_rus.translate(tz_name)} ({tz_code}), {tz_offset}.\n"
                f"Разница во времени с текущим местоположением {dif} ч")
        return text

    # возвращает местное время
    def get_current_time(self):
        local_time = datetime.now(self.timezone_pytz).time()
        return local_time

    # возвращает информацию о городе строкой и ссылку на сайт Википедии
    def get_city_info(self):
        text = f"Город {self.name} находится\nв стране {self.country},\n"
        if self.region:
            ru_region = self.to_rus.translate(self.region)
            text += f"в регионе {ru_region},\n"
        if self.state:
            ru_state = self.to_rus.translate(self.state)
            text += f"в субъкте {ru_state},\n"
            wiki = f"https://ru.wikipedia.org/wiki/{self.name} {ru_state}"
        else:
            wiki = f"https://ru.wikipedia.org/wiki/{self.name} {self.country}"
            print(wiki)
        text += (f"имеет кординаты: широта {round(self.lat, 2)}, долгота {round(self.lng, 2)}.\nБольше информации "
                 f"доступно на сайте")
        link = f'<a href={wiki}>Википедии</a><br>'
        return text, link
