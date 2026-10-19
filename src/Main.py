import datetime
import sqlite3
import sys
import webbrowser
import pyqtgraph

from PyQt6.QtGui import QPixmap, QImage, QDesktopServices, QColor
from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox, QInputDialog, QTableWidgetItem
from PyQt6.QtCore import QTimer

from City import City
from Country import Country
from PlaceSearch import PlaceSearch
from SecondWindow import SecondWindow
from Ui_MainWindow import Ui_MainWindow
from Currency import Currency
from Weather import Weather


class Main(QMainWindow, Ui_MainWindow):
    COUNTRY_DICT = ""
    chosen_city = None
    chosen_country = None
    bargraph = None

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        # добавляем заголовок, фон главного окна и виджетов
        self.setWindowTitle('Города и страны')
        self.setStyleSheet(
            """QMainWindow { background-image:url(resources/background_corr.jpg); background-repeat: no-repeat; 
            background-position: center; } """)
        color = QColor('#fffffffe')
        color.setAlpha(50)
        self.widget.setBackground(color)

        # добавляем список стран
        self.COUNTRY_DICT = PlaceSearch.get_country_list()
        self.countreComboBox.addItem("Не выбрана")
        self.countreComboBox.addItems(self.COUNTRY_DICT.keys())
        # привязываем кнопки к функциям
        self.searchPushButton.clicked.connect(self.get_search_res)
        self.map.clicked.connect(self.show_map)
        self.localTime.clicked.connect(self.show_local_time)
        self.currency_rates.clicked.connect(self.show_currency_rates)
        self.weatherNow.clicked.connect(self.show_current_weather)
        self.weatherToday.clicked.connect(self.show_forecast)
        self.weatherTomorrow.clicked.connect(self.show_forecast)
        self.calculatePB.clicked.connect(self.show_amount)
        self.flag.clicked.connect(self.show_flag)
        self.countryInfo.clicked.connect(self.show_info)
        self.cityInfo.clicked.connect(self.show_info)
        self.history.clicked.connect(self.show_history)
        # создаем объект часов
        self.timer = QTimer(self)
        # настраиваем текстовое поле, чтобы ссылки открывались в браузере и сохраняем формат текста
        self.textBrowser.anchorClicked.connect(QDesktopServices.openUrl)
        self.text_format = self.textBrowser.currentCharFormat()
        # прячем график, таблицу и текстовое поле
        self.widget.setVisible(False)
        self.tableWidget.setVisible(False)
        self.textBrowser.setVisible(False)
        # подлючаемся к базе данных
        self.con = sqlite3.connect("resources/history_db")
        self.cur = self.con.cursor()
        # создаем переменную для объекта дополнительного окна
        self.add_form = ""

    def get_search_res(self):
        # возвращаем первоначальный вид приложения
        self.clear_widgets()
        self.disable_widgets()
        self.chosen_city = None
        self.chosen_country = None
        self.statusBar().showMessage("")
        # считываем введенные данные
        self.country_input = self.countreComboBox.currentText()
        self.city_input = self.cityEntry.text()
        # проверяем ввели ли страну
        got_country = True if self.country_input != "Не выбрана" else False
        # проверяем правильность ввода города
        got_city = True if len(self.city_input) > 2 else False
        # если введено меньше двух букв, просим заполнить снова
        if 0 < len(self.city_input) < 3:
            while not got_city:
                inp, ok_pressed = QInputDialog.getText(self, "Внимание!",
                                                       "Вы ввели слишком мало букв. Введите, пожалуйста, полное "
                                                       "название города.")
                if ok_pressed:
                    if len(inp) > 2:
                        self.cityEntry.setText(inp)
                        self.city_input = inp
                        got_city = True
        # если выбрана только страна
        if got_country and not got_city:
            self.search_by_country()
        # если выбран город и страна
        if got_country and got_city:
            self.search_by_country_and_city()
        # если ищем только по названию города
        if not got_country and got_city:
            self.search_by_city()

    # ищем страну
    def search_by_country(self):
        try:
            country_data = PlaceSearch.find_country(self.country_input)
            if not country_data:
                QMessageBox().warning(self, "Ошибка",
                                      f"К сожалению, не можем найти информацию о стране {self.country_input}.")
            else:
                # создаем объект страны, удаляем объект города
                self.chosen_country = Country(country_data)
                self.chosen_city = ""
                # активируем кнопки для страны
                self.enable_country_widgets()
                # сохраняем в историю поиска
                self.save_search()
                # выводим сообщение в статус бар
                self.statusBar().showMessage(
                    "Страна найдена! Вы можете получить необходимую информацию, используя панель слева.")
        except Exception as e:
            QMessageBox().warning(self, "Ошибка", f"В процессе поиска страны произошла ошибка: {e}.")

    # ищем город в определенной стране
    def search_by_country_and_city(self):
        try:
            # если вдруг страны нет в словаре
            if self.country_input not in list(self.COUNTRY_DICT.keys()):
                QMessageBox().warning(self, "Ошибка",
                                      f"К сожалению, не можем найти информацию о стране {self.country_input}.")
            # иначе достаем код страны
            else:
                country_code = self.COUNTRY_DICT[self.country_input]
                # получаем данные о городе
                city_data = PlaceSearch.find_city_in_country(self.city_input, self.country_input, country_code)
                # если нет такого города в стране, выводим сообщение
                if not city_data:
                    QMessageBox().warning(self, "Ошибка",
                                          f"К сожалению, город {self.city_input} не найден ни в стране {self.country_input}.")
                # если есть, собираем информацию о стране и создаем объект
                else:
                    country_info = PlaceSearch.find_country(self.country_input)
                    # сохраняем объекты города и страны
                    self.chosen_country = Country(country_info)
                    self.chosen_city = City(city_data)
                    # сохраняем историю поиска
                    self.save_search()
                    # активуем все виджеты
                    self.enable_country_widgets()
                    self.enable_city_widgets()
                    # выводим сообщение в статус бар
                    self.statusBar().showMessage(
                        f"Город {self.city_input} в стране {self.country_input} найден! Для получения информации, "
                        f"используя панель слева.")
        except Exception as e:
            QMessageBox().warning(self, "Ошибка", f"В процессе поиска города и страны произошла ошибка: {e}.")

    # определяем в какой стране находится выбранный город
    def search_by_city(self):
        try:
            city_in_countries = PlaceSearch.find_countries_by_city(self.city_input)
            # удаляем непонятные результаты:
            exist_countries = list(self.COUNTRY_DICT.keys())
            for country in city_in_countries:
                if country not in exist_countries:
                    if country not in exist_countries:
                        city_in_countries.remove(country)
            # если город не найден
            if len(city_in_countries) == 0:
                QMessageBox().warning(self, "Ошибка",
                                      f"К сожалению, город {self.city_input} не найден ни в одной стране.")
            # если город найден в одной стране
            elif len(city_in_countries) == 1:
                if city_in_countries[0] not in list(self.COUNTRY_DICT.keys()):
                    QMessageBox().warning(self, "Ошибка",
                                          f"Города {self.city_input} не найден.")
                self.country_input = city_in_countries[0]
                self.countreComboBox.setCurrentText(self.country_input)
                self.search_by_country_and_city()
            # если город есть в нескольких странах
            else:
                self.add_form = SecondWindow(self)
                self.add_form.comboBox.addItems(city_in_countries)
                self.add_form.show()
        # обрабатываем исключения
        except Exception as e:
            QMessageBox().warning(self, "Ошибка", f"В процессе поиска города произошла ошибка: {e}.")

    # возвращаем первоначальное состояние всех виджетов
    def clear_widgets(self):
        self.timer.stop()
        self.clock_label.clear()
        self.flag_label.clear()
        self.tableWidget.clear()
        self.amountEdit.clear()
        self.AmountLcd.display(0)
        self.baseCB.clear()
        self.targetCB.clear()
        self.textBrowser.clear()
        if self.bargraph:
            self.widget.removeItem(self.bargraph)
        self.tableWidget.setVisible(False)
        self.widget.setVisible(False)
        self.textBrowser.setVisible(False)

    # активируем кнопки для страны
    def enable_country_widgets(self):
        for button in self.countryBGroup.buttons():
            button.setEnabled(True)
        self.fill_currency_lists()

    # активируем кнопки для города
    def enable_city_widgets(self):
        for button in self.cityBGroup.buttons():
            button.setEnabled(True)

    # делаем все виджеты неактивными
    def disable_widgets(self):
        for button in self.countryBGroup.buttons():
            button.setEnabled(False)
        for button in self.cityBGroup.buttons():
            button.setEnabled(False)

    def save_search(self):
        # заполняем таблицу стран, если такой страны там еще нет
        country_name = self.chosen_country.name
        region = self.chosen_country.region
        currency = self.chosen_country.currency["ru_name"]
        self.cur.execute('''INSERT OR IGNORE INTO countries(name, region, currency)
                                VALUES(?, ?, ?)''',
                         (country_name, region, currency))
        self.con.commit()
        # заполняем таблицу города, если он выбран и отсутствует в базе данных
        city_name = self.city_input.title()
        if city_name != "":
            self.cur.execute(
                '''INSERT OR IGNORE INTO cities(name, country) 
                        VALUES(?, (SELECT id FROM countries WHERE name = ?))''',
                (city_name, country_name))
            self.con.commit()
        # заполняем таблицу с историей
        created = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cur.execute('''
        WITH    country_id AS (SELECT id FROM countries WHERE name = ?),
                city_id AS (SELECT id
                             FROM cities
                            WHERE name = ?
                            AND country = (SELECT * FROM country_id))
        INSERT
        INTO history (created, country, city)
        VALUES (?,
                (SELECT * FROM country_id),
                (SELECT * FROM city_id)
                                        )''',
                         (country_name, city_name, created))
        self.con.commit()

    def show_map(self):
        if self.chosen_city == "":
            map_url = f"https://www.openstreetmap.org/?mlat={self.chosen_country.lat}&mlon={self.chosen_country.lng}"
        else:
            map_url = f"https://www.openstreetmap.org/?mlat={self.chosen_city.lat}&mlon={self.chosen_city.lng}"
        webbrowser.open(map_url)

    def show_flag(self):
        pict = QImage("resources/flag.png")
        pixmap = QPixmap(pict)
        self.flag_label.setPixmap(pixmap)

    def fill_currency_lists(self):
        self.baseCB.addItems(self.chosen_country.base_curr_list)
        self.targetCB.addItems(self.chosen_country.target_curr_list)

    def show_current_weather(self):
        self.textBrowser.setVisible(True)
        self.widget.setVisible(False)
        self.tableWidget.setVisible(False)
        self.textBrowser.setCurrentCharFormat(self.text_format)
        text = Weather.get_current_weather(self.chosen_city.lat, self.chosen_city.lng)
        self.textBrowser.setText(text)

    def show_forecast(self):
        self.textBrowser.setVisible(True)
        if self.bargraph:
            self.widget.removeItem(self.bargraph)
        self.widget.setVisible(True)
        self.tableWidget.setVisible(True)
        if self.sender() == self.weatherToday:
            res = Weather.get_one_day_forecast(self.chosen_city.lat, self.chosen_city.lng,
                                               self.chosen_city.timezone["name"])[0]
        else:
            res = Weather.get_one_day_forecast(self.chosen_city.lat, self.chosen_city.lng,
                                               self.chosen_city.timezone["name"])[1]
        self.textBrowser.setText(res[0])
        hours = res[1]
        int_hours = list(range(0, 24, 2))
        temp = [int(i) for i in res[2]]
        for_table = res[3]
        titles = ["Темпетарура°C", "Осадки мм", "Облачность %", "Ветер м/с"]
        self.tableWidget.setRowCount(12)
        self.tableWidget.setColumnCount(len(titles))
        self.tableWidget.setHorizontalHeaderLabels(titles)
        self.tableWidget.setVerticalHeaderLabels(hours)
        for i, elem in enumerate(for_table):
            for j, val in enumerate(elem):
                self.tableWidget.setItem(i, j, QTableWidgetItem(str(val)))
        self.tableWidget.resizeColumnsToContents()
        self.bargraph = pyqtgraph.BarGraphItem(x=int_hours, height=temp, width=0.6, brush='#b7d930fe',
                                               setLabel="Температура")
        self.widget.addItem(self.bargraph)

    def show_currency_rates(self):
        self.textBrowser.setVisible(True)
        self.widget.setVisible(False)
        self.tableWidget.setVisible(False)
        message = Currency.get_currency_rates(self.chosen_country.currency)
        if message.startswith("Ошибка"):
            QMessageBox().warning(self, "Внимание!", message)
        else:
            self.textBrowser.setCurrentCharFormat(self.text_format)
            self.textBrowser.setText(message)

    def show_amount(self):
        amount = self.amountEdit.text()
        if not amount.isdigit():
            QMessageBox().warning(self, "Внимание!", "Ошибка ввода, введено не целое число")
        else:
            base_code = self.baseCB.currentText()
            target_code = self.targetCB.currentText()
            res = Currency.calculate_amount(amount, base_code, target_code)
            if res.startswith("Ошибка"):
                QMessageBox().warning(self, "Внимание!", res)
            else:
                self.AmountLcd.display(res)

    def show_local_time(self):
        self.textBrowser.setVisible(True)
        self.widget.setVisible(False)
        self.tableWidget.setVisible(False)
        self.textBrowser.setCurrentCharFormat(self.text_format)
        tz_info = self.chosen_city.get_time_info()
        self.textBrowser.setText(tz_info)
        self.timer.timeout.connect(self.show_clock)
        self.timer.start(1000)

    def show_clock(self):
        clock = self.chosen_city.get_current_time()
        self.clock_label.setText(clock.strftime('%X'))

    def show_info(self):
        self.textBrowser.setVisible(True)
        self.widget.setVisible(False)
        self.tableWidget.setVisible(False)
        self.textBrowser.clear()
        self.textBrowser.setCurrentCharFormat(self.text_format)
        if self.sender() == self.countryInfo:
            text, link = self.chosen_country.get_country_info()
        else:
            text, link = self.chosen_city.get_city_info()
        self.textBrowser.insertPlainText(text)
        self.textBrowser.insertHtml(link)

    def show_history(self):
        self.textBrowser.setVisible(False)
        self.tableWidget.setVisible(True)
        self.widget.setVisible(False)
        result = self.cur.execute("""
                    SELECT history.created,
                        countries.name,
                        COALESCE(cities.name, "Не выбрано"),
                        countries.region,
                        countries.currency 
                    FROM history
                    LEFT JOIN countries ON history.country = countries.id
                    LEFT JOIN cities ON history.city = cities.id
                    ORDER BY history.id DESC
                    """).fetchmany(15)
        titles = ["Время и дата", "Страна", "Город", "Регион", "Валюта"]
        self.tableWidget.setRowCount(len(result))
        self.tableWidget.setColumnCount(len(titles))
        self.tableWidget.setHorizontalHeaderLabels(titles)
        self.tableWidget.setVerticalHeaderLabels([""] * len(result))
        for i, elem in enumerate(result):
            for j, val in enumerate(elem):
                self.tableWidget.setItem(i, j, QTableWidgetItem(str(val)))
        self.tableWidget.resizeColumnsToContents()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Main()
    ex.show()
    sys.exit(app.exec())
