from PyQt6.QtWidgets import QPushButton, QLabel, QComboBox
from PyQt6.QtWidgets import QMainWindow


class SecondWindow(QMainWindow):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        self.setGeometry(600, 400, 300, 160)
        self.setWindowTitle('Выбор страны')
        label = QLabel(f'Город {self.parent().city_input} найден в нескольких странах'
                       f'.\nВыберите нужную: ', self)
        label.resize(250, 40)
        label.move(20, 10)

        self.comboBox = QComboBox(self)
        self.comboBox.resize(250, 20)
        self.comboBox.move(20, 60)

        self.pushButton = QPushButton("Выбрать", self)
        self.pushButton.move(100, 100)
        self.pushButton.resize(100, 30)
        self.pushButton.clicked.connect(self.choose)

    def choose(self):
        # считываем выбранное значение
        country = self.comboBox.currentText()
        # ставим значение в виджет родителя, меняем переменную, запускаем функцию родителя
        self.parent().countreComboBox.setCurrentText(country)
        self.parent().country_input = country
        self.parent().search_by_country_and_city()
        self.close()
