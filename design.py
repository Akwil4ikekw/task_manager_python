from PyQt5.QtWidgets import QMainWindow, QPushButton, QVBoxLayout, QDialog, QLabel, QFrame, QApplication, QScrollArea, QWidget, QLineEdit, QTextEdit, QListWidget, QMessageBox, QHBoxLayout, QTabWidget, QListWidgetItem
import sys
from PyQt5.QtCore import Qt 
from functionality import Functionality
from Task import Task
from PIL import Image
from Team import Team



class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Система управления задачами")
        
        # 1. Сначала инициализируем Functionality
        from functionality import Functionality
        self.func = Functionality(self)
        
        # 2. Создаем центральный виджет и главный layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        
        # 3. Создаем левую панель
        left_panel = QVBoxLayout()
        
        # 4. Сначала добавляем панель пользователя
        self.create_user_panel()
        left_panel.addWidget(self.user_panel)
        
        # 5. Затем добавляем кнопки навигации
        nav_buttons = QVBoxLayout()
        self.create_nav_buttons(nav_buttons)
        left_panel.addLayout(nav_buttons)
        
        # Добавляем растягивающийся элемент
        left_panel.addStretch()
        
        # Создаем правую панель
        right_panel = QVBoxLayout()
        
        # Добавляем заголовок
        title_label = QLabel("Мои задачи")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                padding: 10px;
            }
        """)
        right_panel.addWidget(title_label)
        
        # Создаем область для задач с прокруткой
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: white;
            }
        """)
        
        tasks_widget = QWidget()
        tasks_layout = QVBoxLayout(tasks_widget)
        tasks_layout.addStretch()  # Добавляем растягивающийся элемент
        scroll_area.setWidget(tasks_widget)
        
        right_panel.addWidget(scroll_area)
        
        # Создаем нижнюю панель для кнопки
        bottom_panel = QHBoxLayout()
        bottom_panel.addStretch()  # Добавляем растягивающийся элемент слева
        
        # 5. Создаем маленькую кнопку задачи
        self.create_task_button()
        bottom_panel.addWidget(self.task_button)
        
        right_panel.addLayout(bottom_panel)

        
        # Добавляем панели в главный layout
        main_layout.addLayout(left_panel, 1)
        main_layout.addLayout(right_panel, 4)
        
        self.showMaximized()

    def create_nav_buttons(self, layout):
        """Создание кнопок навигации"""

        spacer = QWidget()
        spacer.setFixedHeight(200)  # Устанавливаем фиксированную высоту 150 пунктов
    
        layout.addWidget(spacer)
        buttons = [
            ("Входящие", self.func.click_input_button),
            ("Календарь", self.func.click_calendar_button),
            ("Бэклог", self.func.click_backlog_button),
            ("Команды", self.func.click_teams_button)
        ]
        
        for text, handler in buttons:
            btn = QPushButton(text)
            btn.setStyleSheet(self.style_button())
            btn.clicked.connect(handler)
            layout.addWidget(btn)

    def create_filters(self, layout):
        """Создание фильтров для задач"""
        filters = ["Все задачи", "Активные", "Завершенные"]
        for filter_name in filters:
            btn = QPushButton(filter_name)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #f0f0f0;
                    border: none;
                    padding: 5px 10px;
                    border-radius: 3px;
                }
                QPushButton:hover {
                    background-color: #e0e0e0;
                }
            """)
            layout.addWidget(btn)
        
        layout.addStretch()

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
        """Создание кнопки для новой задачи"""
        self.task_button = QPushButton("Новая задача", self)
        self.task_button.setFixedSize(120, 30)  # Фиксированный размер кнопки
        self.task_button.clicked.connect(self.func.clicked_create_task)
        self.task_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 5px 10px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        


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

    def create_user_panel(self):
        # Создаем панель пользователя
        self.user_panel = QFrame()  # Сохраняем в self.user_panel
        self.user_panel.setFrameStyle(QFrame.StyledPanel)
        
        # Создаем фрейм для панели пользователя
        user_panel = QFrame(self)
        user_panel.setGeometry(20, 20, 200, 200)
        user_panel.setStyleSheet("""
            QFrame {
                background-color: #f0f0f0;
                border: 2px solid #4CAF50;
                border-radius: 5px;
            }
        """)

        # Создаем layout для панели
        layout = QVBoxLayout(user_panel)

        # Добавляем метку "Пользователь:"
        title_label = QLabel("Пользователь:", user_panel)
        title_label.setStyleSheet("""
            QLabel {
                color: #333;
                font-weight: bold;
                font-size: 14px;
            }
        """)
        layout.addWidget(title_label)

        # Добавляем имя пользователя
        self.username_label = QLabel("Не авторизован", user_panel)
        self.username_label.setStyleSheet("""
            QLabel {
                color: #4CAF50;
                font-size: 12px;
                padding: 5px;
            }
        """)
        layout.addWidget(self.username_label)

        # Кнопка управления командами
        teams_button = QPushButton("Управление командами", user_panel)
        teams_button.clicked.connect(self.func.click_teams_button)
        teams_button.setStyleSheet(self.style_button())
        layout.addWidget(teams_button)

        # Кнопка выхода
        logout_button = QPushButton("Выйти", user_panel)
        logout_button.clicked.connect(self.logout)
        logout_button.setStyleSheet(self.style_button())
        layout.addWidget(logout_button)

        layout.addStretch()
        user_panel.setLayout(layout)

    def update_user_panel(self):
        """Обновляет информацию о пользователе на панели"""
        current_user = self.func.get_current_user()
        if current_user:
            self.username_label.setText(f"{current_user['username']}\n{current_user['email']}")
        else:
            self.username_label.setText("Не авторизован")

    def logout(self):
        """Обработчик выхода из системы"""
        self.func.logout()
        self.func.show_login_window()
        self.update_user_panel()

#     def setup_teams_tab(self):
#         teams_widget = QWidget()
#         layout = QVBoxLayout()
        
#         # Кнопка создания команды
#         create_team_btn = QPushButton("Создать команду")
#         create_team_btn.clicked.connect(self.show_create_team_dialog)
#         layout.addWidget(create_team_btn)
        
#         # Список команд
#         self.teams_list = QListWidget()
#         self.teams_list.itemClicked.connect(self.on_team_selected)
#         layout.addWidget(self.teams_list)
        
#         teams_widget.setLayout(layout)
#         self.tab_widget.addTab(teams_widget, "Команды")
        
#         # Обновляем список команд
#         self.update_teams_list()
    
    def show_create_team_dialog(self):
        dialog = CreateTeamDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            team_name = dialog.name_edit.text()
            team_description = dialog.description_edit.toPlainText()
            
            if team_name:
                team = Team(team_name, team_description)
                team_id = self.func.db.create_team(team)
                # Добавляем создателя как админа
                self.func.db.add_team_member(team_id, self.func.current_user_id, 'admin')
                self.update_teams_list()
                QMessageBox.information(self, "Успех", "Команда успешно создана!")
    
    def update_teams_list(self):
        self.teams_list.clear()
        teams = self.func.db.get_all_teams()
        for team in teams:
            self.teams_list.addItem(f"{team[1]} (Участников: {team[3]})")
            self.teams_list.item(self.teams_list.count() - 1).setData(Qt.UserRole, team[0])
    
    def on_team_selected(self, item):
        team_id = item.data(Qt.UserRole)
        team_members = self.func.db.get_team_members(team_id)
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Управление командой")
        layout = QVBoxLayout()
        
        # Список участников
        members_label = QLabel("Участники команды:")
        layout.addWidget(members_label)
        
        members_list = QListWidget()
        for member in team_members:
            members_list.addItem(f"{member[1]} ({member[2]})")
        layout.addWidget(members_list)
        
        # Кнопка приглашения
        invite_btn = QPushButton("Пригласить пользователя")
        invite_btn.clicked.connect(lambda: self.show_invite_dialog(team_id))
        layout.addWidget(invite_btn)
        
        dialog.setLayout(layout)
        dialog.exec_()
    
    def show_invite_dialog(self):
        if not self.teams_list.currentItem():
            QMessageBox.warning(self, "Предупреждение", "Выберите команду!")
            return
        
        team_id = self.teams_list.currentItem().data(Qt.UserRole)
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Пригласить участника")
        layout = QVBoxLayout()
        
        # Поле для ввода email
        email_input = QLineEdit()
        email_input.setPlaceholderText("Введите email пользователя")
        layout.addWidget(email_input)
        
        # Кнопки
        buttons_layout = QHBoxLayout()
        invite_btn = QPushButton("Пригласить")
        cancel_btn = QPushButton("Отмена")
        buttons_layout.addWidget(invite_btn)
        buttons_layout.addWidget(cancel_btn)
        layout.addLayout(buttons_layout)
        
        dialog.setLayout(layout)
        
        def invite_user():
            email = email_input.text().strip()
            if not email:
                QMessageBox.warning(dialog, "Предупреждение", "Введите email пользователя")
                return
            
            user = self.func.db.get_user_by_email(email, team_id)
            if user is None:
                QMessageBox.warning(dialog, "Ошибка", "Пользователь не найден или уже состоит в команде")
                return
            
            if self.func.db.invite_user_to_team(user[0], team_id):
                QMessageBox.information(self, "Успех", "Пользователь успешно добавлен в команду!")
                self.update_teams_list()
                dialog.accept()
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось добавить пользователя в команду")
        
        invite_btn.clicked.connect(invite_user)
        cancel_btn.clicked.connect(dialog.reject)
        
        dialog.exec_()

class CreateTeamDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Создание команды")
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Название команды
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Название команды")
        layout.addWidget(self.name_edit)
        
        # Описание команды
        self.description_edit = QTextEdit()
        self.description_edit.setPlaceholderText("Описание команды")
        layout.addWidget(self.description_edit)
        
        # Кнопки
        buttons_layout = QHBoxLayout()
        self.create_button = QPushButton("Создать")
        self.cancel_button = QPushButton("Отмена")
        buttons_layout.addWidget(self.create_button)
        buttons_layout.addWidget(self.cancel_button)
        
        layout.addLayout(buttons_layout)

        self.setLayout(layout)
        
        # Подключаем сигналы
        self.create_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

class InviteUserDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Пригласить пользователя")
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        
        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText("Имя пользователя")
        layout.addWidget(self.username_edit)
        
        buttons_layout = QHBoxLayout()
        self.invite_button = QPushButton("Пригласить")
        self.cancel_button = QPushButton("Отмена")
        buttons_layout.addWidget(self.invite_button)
        buttons_layout.addWidget(self.cancel_button)
        
        layout.addLayout(buttons_layout)
        self.setLayout(layout)
        
        self.invite_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)
