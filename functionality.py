from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QLabel, QInputDialog, QPushButton, QWidget, QCheckBox, QLineEdit, QHBoxLayout, QMessageBox, QCalendarWidget, QListWidget, QFileDialog, QListWidgetItem, QTabWidget, 
                             QTextEdit)
from PyQt5.QtCore import QDate, Qt
from PyQt5.QtGui import QIcon, QPixmap
import os
from database import Database
from Task import Task
# from Project import Project
# from task_history import TaskHistory
# from Team import Team
from datetime import datetime
import re  # Добавьте в начало файла
from Team import Team
import shutil

# from UserTeam import UserTeam



class Functionality:
    def __init__(self, window):
        self.window = window
        self.db = Database()
        self.current_user = None  # Добавляем атрибут для хранения текущего пользователя
        self.current_team = None  # Добавляем атрибут для хранения текущей команды
        
    def set_current_team(self, team_id: int, team_name: str):
        """Установить текущую команду"""
        self.current_team = {'id': team_id, 'name': team_name}
        # Обновляем состояние кнопки
        self.window.update_select_team_button()

    def get_current_team(self):
        """Получить текущую команду"""
        return self.current_team

    def get_current_user(self):
        """Получить текущего пользователя"""
        return self.current_user
        
    def is_authenticated(self):
        """Проверить, авторизован ли пользователь"""
        return self.current_user is not None

    def logout(self):
        """Выход из системы"""
        self.current_user = None
        self.current_team = None  # Сбрасываем текущую команду
        self.window.update_select_team_button()
        
    def click_input_button(self):
        dlg = QDialog(self.window)
        dlg.setWindowTitle("Сообщение")
        layout = QVBoxLayout()
        label = QLabel("Кнопка Входящие была нажата.")
        layout.addWidget(label)
        dlg.setLayout(layout)
        dlg.exec()
        
    def click_teams_button(self):
        if not self.is_authenticated():
            QMessageBox.warning(self.window, "Ошибка", "Необходимо войти в систему")
            return
        
        dlg = QDialog(self.window)
        dlg.setWindowTitle("Мои команды")
        dlg.resize(400, 500)
        
        layout = QVBoxLayout()
        
        # Получаем список команд пользователя
        teams = self.db.get_user_teams(self.current_user['user_id'])
        
        if teams:
            # Создаем список для отображения команд
            teams_list = QListWidget()
            for team in teams:
                team_id, name, description, role = team
                item = QListWidgetItem(f"{name} ({role})")
                item.setData(Qt.UserRole, team_id)
                item.setData(Qt.UserRole + 1, name)
                teams_list.addItem(item)
            
            # Исправленный обработчик
            teams_list.itemClicked.connect(
                lambda item: self.on_team_selected(
                    item.data(Qt.UserRole),  # team_id
                    item.data(Qt.UserRole + 1)  # team_name
                )
            )
            layout.addWidget(teams_list)
        else:
            # Если команд нет, показываем сообщение
            no_teams_label = QLabel("Пока вы не состоите ни в каких командах")
            no_teams_label.setStyleSheet("""
                QLabel {
                    color: #666;
                    padding: 20px;
                    font-size: 14px;
                }
            """)
            no_teams_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(no_teams_label)
        
        # Кнопка создания команды
        create_team_btn = QPushButton("Создать команду")
        create_team_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                margin-top: 10px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        create_team_btn.clicked.connect(lambda: self.create_team_dialog())
        layout.addWidget(create_team_btn)
        
        dlg.setLayout(layout)
        dlg.exec_()

    def click_calendar_button(self):
        dlg = QDialog(self.window)
        dlg.setWindowTitle("Сообщение")
        layout = QVBoxLayout()
        label = QLabel("Кнопка Календарь была нажата.")
        layout.addWidget(label)
        dlg.setLayout(layout)
        dlg.exec()

    def click_backlog_button(self):
        dlg = QDialog(self.window)
        dlg.setWindowTitle("Сообщение")
        layout = QVBoxLayout()
        label = QLabel("Кнопка Бэклог была нажата.")
        layout.addWidget(label)
        dlg.setLayout(layout)
        dlg.exec()

    def clicked_create_task(self):
        if not self.is_authenticated():
            QMessageBox.warning(self.window, "Ошибка", "Необходимо войти в систему")
            return
            
        dlg = QDialog(self.window)
        dlg.setWindowTitle("Создание задачи")
        dlg.resize(500, 400)
        
        layout = QVBoxLayout()
        
        # Название задачи
        task_name = QLineEdit()
        task_name.setPlaceholderText("Введите название задачи")
        
        # Описание
        description = QLineEdit()
        description.setPlaceholderText("Описание задачи")
        description.setFixedHeight(100)
        
        # Дедлайн с временем
        deadline_layout = QHBoxLayout()
        deadline_label = QLabel("Дедлайн:")
        
        # Поле для даты
        deadline_date = QLineEdit()
        deadline_date.setReadOnly(True)
        deadline_date.setPlaceholderText("Выберите дату")
        deadline_date.setFixedWidth(100)
        
        # Поле для времени
        from PyQt5.QtWidgets import QTimeEdit
        from PyQt5.QtCore import QTime
        deadline_time = QTimeEdit()
        deadline_time.setTime(QTime.currentTime())  # Устанавливаем текущее время по умолчанию
        deadline_time.setDisplayFormat("HH:mm")
        deadline_time.setFixedWidth(70)
        
        # Кнопка календаря
        calendar_button = QPushButton()
        icon_path = os.path.join('icons', 'icons8-calendar-32.png')
        if os.path.exists(icon_path):
            calendar_button.setIcon(QIcon(icon_path))
        else:
            calendar_button.setText("📅")
        calendar_button.setFixedSize(32, 32)
        
        deadline_layout.addWidget(deadline_label)
        deadline_layout.addWidget(deadline_date)
        deadline_layout.addWidget(deadline_time)
        deadline_layout.addWidget(calendar_button)
        deadline_layout.addStretch()
        
        # Добавляем выбор времени уведомления
        notification_layout = QHBoxLayout()
        notification_label = QLabel("Уведомить за:")
        
        # Выпадающий список с предустановленными значениями
        from PyQt5.QtWidgets import QComboBox
        notification_preset = QComboBox()
        notification_preset.addItems(["В момент дедлайна", "5 минут", "10 минут", "15 минут", "30 минут", "1 час", "Другое..."])
        
        # Поле для ввода произвольного количества минут
        notification_custom = QLineEdit()
        notification_custom.setPlaceholderText("минут")
        notification_custom.setFixedWidth(60)
        notification_custom.hide()  # Изначально скрыто
        
        def on_preset_changed(text):
            if text == "Другое...":
                notification_custom.show()
            else:
                notification_custom.hide()
            
        notification_preset.currentTextChanged.connect(on_preset_changed)
        
        notification_layout.addWidget(notification_label)
        notification_layout.addWidget(notification_preset)
        notification_layout.addWidget(notification_custom)
        notification_layout.addStretch()
        
        # Календарь
        calendar = QCalendarWidget()
        # Устанавливаем минимальную дату как сегодня
        calendar.setMinimumDate(QDate.currentDate())
        calendar.hide()
        
        def toggle_calendar():
            if calendar.isHidden():
                # При открытии календаря устанавливаем текущую дату как выбранную
                if not deadline_date.text():
                    calendar.setSelectedDate(QDate.currentDate())
                calendar.show()
            else:
                calendar.hide()
            
        def select_date():
            selected_date = calendar.selectedDate()
            if selected_date >= QDate.currentDate():
                deadline_date.setText(selected_date.toString("dd.MM.yyyy"))
                calendar.hide()
            else:
                QMessageBox.warning(dlg, "Ошибка", "Нельзя выбрать прошедшую дату")
        
        calendar_button.clicked.connect(toggle_calendar)
        calendar.clicked.connect(select_date)
        
        # Кнопка создания
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        create_button = QPushButton("Создать задачу")
        create_button.setFixedSize(100, 30)
        
        def on_create_button_clicked():
            if not task_name.text():
                QMessageBox.warning(dlg, "Ошибка", "Введите название задачи")
                return
                
            if not deadline_date.text():
                QMessageBox.warning(dlg, "Ошибка", "Выберите дату дедлайна")
                return
                
            try:
                # Преобразуем строки в timestamp
                deadline_str = f"{deadline_date.text()} {deadline_time.time().toString('HH:mm')}"
                deadline_dt = datetime.strptime(deadline_str, "%d.%m.%Y %H:%M")
                deadline_timestamp = deadline_dt.timestamp()
                
                # Вычисляем время уведомления
                notification_timestamp = deadline_timestamp  # По умолчанию равно дедлайну
                
                if notification_preset.currentText() != "В момент дедлайна":
                    if notification_preset.currentText() == "Другое...":
                        try:
                            minutes = int(notification_custom.text())
                            if minutes <= 0:
                                raise ValueError()
                        except ValueError:
                            QMessageBox.warning(dlg, "Ошибка", "Введите корректное количество минут")
                            return
                    else:
                        text = notification_preset.currentText()
                        if "час" in text:
                            minutes = 60
                        else:
                            minutes = int(text.split()[0])
                    
                    from datetime import timedelta
                    notification_dt = deadline_dt - timedelta(minutes=minutes)
                    notification_timestamp = notification_dt.timestamp()
                
                # Создаем задачу
                task = Task(
                    name=task_name.text(),
                    description=description.text(),
                    user_id=self.current_user['user_id'],
                    status=False,
                    deadline=deadline_timestamp,
                    start=datetime.now().timestamp(),
                    end=None,
                    team_id=None,
                    project_id=None,
                    task_id=None,
                    priority=1,
                    notification_time=notification_timestamp,
                    notified=False
                )
                
                # Сохраняем задачу в базу данных
                task_id = self.db.add_task(task)
                if task_id:
                    notification_str = (
                        "в момент дедлайна" if notification_timestamp == deadline_timestamp 
                        else datetime.fromtimestamp(notification_timestamp).strftime("%d.%m.%Y %H:%M")
                    )
                    QMessageBox.information(dlg, "Успех", 
                        f"Задача создана. Уведомление придет {notification_str}")
                    dlg.accept()
                else:
                    QMessageBox.critical(dlg, "Ошибка", "Не удалось сохранить задачу в базе данных")
            except Exception as e:
                QMessageBox.critical(dlg, "Ошибка", f"Ошибка при создании задачи: {str(e)}")
        
        create_button.clicked.connect(on_create_button_clicked)
        button_layout.addWidget(create_button)
        
        # Добавляем все элементы в layout
        layout.addWidget(task_name)
        layout.addWidget(description)
        layout.addLayout(deadline_layout)
        layout.addWidget(calendar)
        layout.addLayout(notification_layout)
        layout.addStretch()
        layout.addLayout(button_layout)
        
        dlg.setLayout(layout)
        dlg.exec()
        
    def validate_email(self, email: str) -> bool:
        """Проверка валидности email"""
        # Паттерн для проверки email
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
        
    def show_login_window(self):
        dlg = QDialog(self.window)
        dlg.setWindowTitle("Вход в систему")
        dlg.resize(400, 200)
        
        layout = QVBoxLayout()
        
        email = QLineEdit()
        email.setPlaceholderText("Email")
        
        password = QLineEdit()
        password.setPlaceholderText("Пароль")
        password.setEchoMode(QLineEdit.Password)
        
        button_layout = QHBoxLayout()
        
        login_button = QPushButton("Войти")
        register_button = QPushButton("Регистрация")
        
        def try_login():
            if not all([email.text(), password.text()]):
                QMessageBox.warning(dlg, "Ошибка", "Все поля должны быть заполнены")
                return

            if not self.validate_email(email.text()):
                QMessageBox.warning(dlg, "Ошибка", "Некорректный формат email")
                return

            try:
                user_data = self.db.login_user(email.text(), password.text())
                if user_data:
                    self.current_user = {
                        'user_id': user_data[0],
                        'username': user_data[1],
                        'email': user_data[2],
                        'created_at': user_data[3]
                    }
                    self.window.update_user_panel()
                    dlg.accept()
                else:
                    QMessageBox.warning(dlg, "Ошибка", "Неверный email или пароль")
            except Exception as e:
                QMessageBox.critical(dlg, "Ошибка", f"Ошибка при входе: {str(e)}")
        
        def open_registration():
            dlg.close()
            self.show_registration_window()
        
        login_button.clicked.connect(try_login)
        register_button.clicked.connect(open_registration)
        
        button_layout.addWidget(login_button)
        button_layout.addWidget(register_button)
        
        layout.addWidget(email)
        layout.addWidget(password)
        layout.addLayout(button_layout)
        
        dlg.setLayout(layout)
        return dlg.exec()
        
    def show_registration_window(self):
        dlg = QDialog(self.window)
        dlg.setWindowTitle("Регистрация")
        dlg.resize(400, 200)
        
        layout = QVBoxLayout()
        
        username = QLineEdit()
        username.setPlaceholderText("Имя пользователя")
        
        email = QLineEdit()
        email.setPlaceholderText("Email")
        
        password = QLineEdit()
        password.setPlaceholderText("Пароль")
        password.setEchoMode(QLineEdit.Password)
        
        confirm_password = QLineEdit()
        confirm_password.setPlaceholderText("Подтвердите пароль")
        confirm_password.setEchoMode(QLineEdit.Password)
        
        register_button = QPushButton("Зарегистрироваться")
        
        def try_register():
            if not all([username.text(), email.text(), password.text()]):
                QMessageBox.warning(dlg, "Ошибка", "Все поля должны быть заполнены")
                return

            if not self.validate_email(email.text()):
                QMessageBox.warning(dlg, "Ошибка", "Некорректный формат email")
                return

            if password.text() != confirm_password.text():
                QMessageBox.warning(dlg, "Ошибка", "Пароли не совпадают")
                return
                
            try:
                # Проверяем, не занят ли email
                if self.db.check_email_exists(email.text()):
                    QMessageBox.warning(dlg, "Ошибка", "Этот email уже зарегистрирован")
                    return
                    
                # Регистрируем пользователя
                user_data = self.db.register_user(
                    username.text(),
                    email.text(),
                    password.text()
                )
                
                if user_data:
                    self.current_user = {
                        'user_id': user_data[0],
                        'username': user_data[1],
                        'email': user_data[2],
                        'created_at': user_data[3]
                    }
                    self.window.update_user_panel()
                    QMessageBox.information(dlg, "Успех", "Регистрация успешно завершена!")
                    dlg.accept()
                
            except Exception as e:
                QMessageBox.critical(dlg, "Ошибка", f"Ошибка при регистрации: {str(e)}")
        
        register_button.clicked.connect(try_register)
        
        layout.addWidget(username)
        layout.addWidget(email)
        layout.addWidget(password)
        layout.addWidget(confirm_password)
        layout.addWidget(register_button)
        
        dlg.setLayout(layout)
        return dlg.exec()
        
    def create_team_dialog(self):
        dlg = QDialog(self.window)
        dlg.setWindowTitle("Создание команды")
        dlg.resize(400, 300)
        
        layout = QVBoxLayout()
        
        # Поле для названия команды
        name_label = QLabel("Название команды:")
        layout.addWidget(name_label)
        
        name_edit = QLineEdit()
        name_edit.setPlaceholderText("Введите название команды")
        layout.addWidget(name_edit)
        
        # Выбор иконки
        icon_label = QLabel("Иконка команды:")
        layout.addWidget(icon_label)
        
        icon_preview = QLabel()
        icon_preview.setFixedSize(64, 64)
        icon_preview.setStyleSheet("border: 1px solid #ccc;")
        layout.addWidget(icon_preview)
        
        icon_path = [""]  # Используем список для хранения пути к иконке
        
        def select_icon():
            file_name, _ = QFileDialog.getOpenFileName(
                dlg,
                "Выберите иконку",
                "",
                "Images (*.png *.jpg *.jpeg *.ico);;All Files (*)"
            )
            if file_name:
                # Создаем директорию для иконок, если её нет
                icons_dir = os.path.join(os.path.dirname(__file__), 'team_icons')
                os.makedirs(icons_dir, exist_ok=True)
                
                # Копируем файл в директорию иконок
                icon_filename = f"team_icon_{datetime.now().strftime('%Y%m%d_%H%M%S')}{os.path.splitext(file_name)[1]}"
                icon_path[0] = os.path.join(icons_dir, icon_filename)
                shutil.copy2(file_name, icon_path[0])
                
                # Показываем превью
                pixmap = QPixmap(file_name)
                icon_preview.setPixmap(pixmap.scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        
        select_icon_btn = QPushButton("Выбрать иконку")
        select_icon_btn.clicked.connect(select_icon)
        layout.addWidget(select_icon_btn)
        
        # Кнопка создания команды
        create_btn = QPushButton("Создать команду")
        create_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                margin-top: 10px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        
        def try_create_team():
            if not name_edit.text():
                QMessageBox.warning(dlg, "Ошибка", "Введите название команды")
                return
            
            if not icon_path[0]:
                QMessageBox.warning(dlg, "Ошибка", "Выберите иконку команды")
                return
            
            try:
                team_id = self.db.create_team(name_edit.text(), icon_path[0])
                # Добавляем создателя как админа команды
                self.db.add_team_member(team_id, self.current_user['user_id'], 'admin')
                QMessageBox.information(dlg, "Успех", "Команда успешно создана!")
                dlg.accept()
            except Exception as e:
                QMessageBox.critical(dlg, "Ошибка", f"Ошибка при создании команды: {str(e)}")
        
        create_btn.clicked.connect(try_create_team)
        layout.addWidget(create_btn)
        
        dlg.setLayout(layout)
        return dlg.exec()

    def on_team_selected(self, team_id: int, team_name: str):
        """Обработка выбора команды"""
        dlg = QDialog(self.window)
        dlg.setWindowTitle(f"Команда: {team_name}")
        dlg.resize(600, 400)
        
        layout = QVBoxLayout()
        
        # Кнопка выбора команды
        select_team_btn = QPushButton("Выбрать команду")
        select_team_btn.setStyleSheet(self.window.style_button())
        select_team_btn.clicked.connect(lambda: self.set_current_team(team_id, team_name))
        layout.addWidget(select_team_btn)
        
        # Создаем вкладки
        tabs = QTabWidget()
        
        # Вкладка проектов
        projects_tab = QWidget()
        projects_layout = QVBoxLayout()
        
        # Список проектов
        projects = self.db.get_team_projects(team_id)
        if projects:
            projects_list = QListWidget()
            for project in projects:
                project_id, name, description, created_at = project
                item_text = f"{name}"
                if description:
                    item_text += f"\n{description}"
                projects_list.addItem(item_text)
            projects_layout.addWidget(projects_list)
        else:
            no_projects_label = QLabel("В команде пока нет проектов")
            no_projects_label.setAlignment(Qt.AlignCenter)
            projects_layout.addWidget(no_projects_label)
        
        # Кнопка создания проекта
        create_project_btn = QPushButton("Создать проект")
        create_project_btn.setStyleSheet(self.window.style_button())
        create_project_btn.clicked.connect(lambda: self.show_create_project_dialog(team_id))
        projects_layout.addWidget(create_project_btn)
        
        projects_tab.setLayout(projects_layout)
        tabs.addTab(projects_tab, "Проекты")
        
        # Вкладка участников
        members_tab = QWidget()
        members_layout = QVBoxLayout()
        
        members = self.db.get_team_members(team_id)
        members_list = QListWidget()
        for member in members:
            user_id, username, role = member
            members_list.addItem(f"{username} ({role})")
        members_layout.addWidget(members_list)
        
        # Кнопка приглашения участников
        invite_btn = QPushButton("Пригласить участника")
        invite_btn.setStyleSheet(self.window.style_button())
        invite_btn.clicked.connect(lambda: self.show_invite_dialog(team_id))
        members_layout.addWidget(invite_btn)
        
        members_tab.setLayout(members_layout)
        tabs.addTab(members_tab, "Участники")
        
        layout.addWidget(tabs)
        dlg.setLayout(layout)
        dlg.exec_()

    def show_create_project_dialog(self, team_id: int):
        """Диалог создания проекта"""
        dlg = QDialog(self.window)
        dlg.setWindowTitle("Создание проекта")
        layout = QVBoxLayout()
        
        name_edit = QLineEdit()
        name_edit.setPlaceholderText("Название проекта")
        layout.addWidget(name_edit)
        
        desc_edit = QTextEdit()
        desc_edit.setPlaceholderText("Описание проекта")
        layout.addWidget(desc_edit)
        
        create_btn = QPushButton("Создать")
        create_btn.setStyleSheet(self.window.style_button())
        
        def try_create_project():
            if not name_edit.text():
                QMessageBox.warning(dlg, "Ошибка", "Введите название проекта")
                return
            
            try:
                self.db.create_project(name_edit.text(), desc_edit.toPlainText(), team_id)
                QMessageBox.information(dlg, "Успех", "Проект успешно создан!")
                dlg.accept()
            except Exception as e:
                QMessageBox.critical(dlg, "Ошибка", f"Ошибка при создании проекта: {str(e)}")
        
        create_btn.clicked.connect(try_create_project)
        layout.addWidget(create_btn)
        
        dlg.setLayout(layout)
        dlg.exec_()

    def show_invite_dialog(self, team_id: int):
        """Диалог приглашения участника"""
        dlg = QDialog(self.window)
        dlg.setWindowTitle("Пригласить участника")
        layout = QVBoxLayout()
        
        email_edit = QLineEdit()
        email_edit.setPlaceholderText("Email пользователя")
        layout.addWidget(email_edit)
        
        invite_btn = QPushButton("Пригласить")
        invite_btn.setStyleSheet(self.window.style_button())
        
        def try_invite_user():
            if not email_edit.text():
                QMessageBox.warning(dlg, "Ошибка", "Введите email пользователя")
                return
            
            try:
                user_data = self.db.get_user_by_email(email_edit.text(), team_id)
                if user_data:
                    self.db.add_team_member(team_id, user_data[0])
                    QMessageBox.information(dlg, "Успех", "Пользователь приглашен в команду!")
                    dlg.accept()
                else:
                    QMessageBox.warning(dlg, "Ошибка", "Пользователь не найден")
            except Exception as e:
                QMessageBox.critical(dlg, "Ошибка", f"Ошибка при приглашении пользователя: {str(e)}")
        
        invite_btn.clicked.connect(try_invite_user)
        layout.addWidget(invite_btn)
        
        dlg.setLayout(layout)
        dlg.exec_()



#TODO: 1. Сделать атворизацию пользователя и чтобы совершать действия от его лица (комментарии, созбании проетков, создание задач)        
#TODO  2. Сделать создание задач (использование иконок, для записи в календарь, запись приоритета с помощью SelectBox, Дата дедлайна, напомининие поставить по дефолту как задача сейчас по времени в тот момент и уведомлять)
#TODO  3. сделать вывод проектов и возомжно по ним нажимать и редактировать как в было в прошлой итерации
#TODO  4. Сделать историю где будет написаны изменения и написано кто внес изменения.

#На данный момент реализована регистрация с записью в бд SadSmile