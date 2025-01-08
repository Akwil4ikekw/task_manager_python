from PyQt5.QtWidgets import QMainWindow, QPushButton, QVBoxLayout, QDialog, QLabel, QFrame, QApplication, QScrollArea, QWidget
import sys
from functionality import Functionality





class Window(QMainWindow):
    def __init__(self):
        super().__init__()

        # Инициализация интерфейса
        self.setWindowTitle("Менеджер задач")
        self.setGeometry(100, 100, 600, 400)


        # Создание объектов для работы с функционалом
        self.func = Functionality(self)

        # Создание кнопок
        self.input_button()
        self.calendar_button()
        self.backlog_button()
       # self.create_project_block()
        self.create_task_button()
        # Отображение окна
        self.showMaximized()



    # Метод для кнопки "Входящие"
    def input_button(self):
        button = QPushButton("Входящие", self)
        button.setGeometry(20, 200, 120, 30)
        button.clicked.connect(self.func.click_input_button)
        button.setStyleSheet(self.style_button())

    # Метод для кнопки "Календарь"
    def calendar_button(self):
        button = QPushButton("Календарь", self)
        button.setGeometry(20, 250, 120, 30)
        button.clicked.connect(self.func.click_calendar_button)
        button.setStyleSheet(self.style_button())

    # Метод для кнопки "Бэклог"
    def backlog_button(self):
        button = QPushButton("Бэклог", self)
        button.setGeometry(20, 300, 120, 30)
        button.clicked.connect(self.func.click_backlog_button)
        button.setStyleSheet(self.style_button())

    # Метод для создания блока проектов
    # def create_project_block(self):
    #     project_block = QFrame(self)
    #     project_block.setGeometry(20, 460, 250, 450)
    #     project_block.setFrameShape(QFrame.StyledPanel)
    #     project_block.setStyleSheet("background-color: #f0f0f0; border: 2px solid #4CAF50;")
    #     layout = QVBoxLayout()

    #     # Список проектов
    #     self.project_list_area = QScrollArea(self)
    #     self.project_list_area.setWidgetResizable(True)
    #     self.project_list_widget = QWidget()
    #     self.project_list_layout = QVBoxLayout()
    #     self.project_list_widget.setLayout(self.project_list_layout)
    #     self.project_list_area.setWidget(self.project_list_widget)

    #     layout.addWidget(self.project_list_area)

    #     # Кнопка добавления проекта
    #     self.projects_label = QLabel("Проекты:")
    #     layout.addWidget(self.projects_label)

    #     button = QPushButton("Добавить проект", self)

    #     layout.addWidget(button)

    #     project_block.setLayout(layout)

    #     # Сохранение ссылки на layout для последующего обновления
    #     self.project_list_layout = self.project_list_layout

    #     # Обновление списка проектов
    #     self.func.update_projects()
    


    def create_task_button(self):
        button = QPushButton("Новая задача", self)
        button.setGeometry(1020, 900, 120, 30)
        button.clicked.connect(self.func.clicked_create_task)
        button.setStyleSheet(self.style_button())
        


    # Стиль кнопки
    def style_button(self):
        return """
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """
