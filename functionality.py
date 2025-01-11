from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QLabel, QInputDialog, QPushButton, QWidget, QCheckBox, QLineEdit, QHBoxLayout, QMessageBox, QCalendarWidget, QListWidget, QFileDialog, QListWidgetItem, QTabWidget, 
                             QTextEdit, QComboBox, QTimeEdit)
from PyQt5.QtCore import QDate, Qt, QTime, QSize, QTimer
from PyQt5.QtGui import QIcon, QPixmap
import os
from database import Database
from Task import Task
from PyQt5.QtCore import QTimer
# from Project import Project
# from task_history import TaskHistory
# from Team import Team
from datetime import datetime, timedelta
import re  # Добавьте в начало файла
from Team import Team
from kanban_board import KanbanBoard
import shutil
from PIL import Image  # Для проверки изображений

# from UserTeam import UserTeam



class Functionality:
    def __init__(self, window):
        self.window = window
        self.db = Database()
        self.current_user = None  # Добавляем атрибут для хранения текущего пользователя
        self.current_team = None  # Добавляем атрибут для хранения текущей команды
        self.window.current_project_id = None  # Добавляем инициализацию
        
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
        try:
            self.current_user = None
            self.current_team = None
            self.window.current_project_id = None
            self.window.update_user_panel()
            if hasattr(self.window, 'update_select_team_button'):
                self.window.update_select_team_button()
        except Exception as e:
            print(f"Ошибка при выходе: {str(e)}")
            import traceback
            traceback.print_exc()
        
    def click_input_button(self):
        """Показать канбан доску со всеми задачами"""
        if not self.is_authenticated():
            QMessageBox.warning(self.window, "Ошибка", "Необходимо войти в систему")
            return
        
        # Создаем диалог с канбан доской
        dialog = QDialog(self.window)
        dialog.setWindowTitle("Мои задачи")
        dialog.resize(1200, 800)
        
        layout = QVBoxLayout()
        
        # Создаем канбан доску
        kanban = KanbanBoard()
        
        # Получаем все задачи пользователя
        try:
            tasks = self.db.get_user_tasks(self.current_user['user_id'])
            
            # Распределяем задачи по колонкам
            for task in tasks:
                if task.status == False:
                    kanban.add_task(task, "todo")
                elif task.status == True:
                    kanban.add_task(task, "done")
        except Exception as e:
            print(f"Ошибка при загрузке задач: {e}")
        
        layout.addWidget(kanban)
        dialog.setLayout(layout)
        dialog.exec_()
        
    def click_teams_button(self):
        if not self.is_authenticated():
            QMessageBox.warning(self.window, "Ошибка", "Необходимо войти в систему")
            return
        
        # Закрываем предыдущее окно команд, если оно открыто
        if hasattr(self, 'teams_dialog') and self.teams_dialog is not None:
            self.teams_dialog.close()
        
        self.teams_dialog = QDialog(self.window)
        self.teams_dialog.setWindowTitle("Мои команды")
        self.teams_dialog.resize(400, 500)
        
        layout = QVBoxLayout()
        
        # Получаем список команд пользователя
        teams = self.db.get_user_teams(self.current_user['user_id'])
        
        if teams:
            # Создаем список для отображения команд
            teams_list = QListWidget()
            teams_list.setIconSize(QSize(40, 40))  # Устанавливаем размер иконок
            
            for team in teams:
                team_id, name, description, role, icon_path, member_count = team  # Добавлен member_count
                
                # Создаем виджет для элемента списка
                item_widget = QWidget()
                item_layout = QHBoxLayout()
                item_widget.setLayout(item_layout)
                
                # Аватар команды
                avatar_label = QLabel()
                avatar_label.setFixedSize(40, 40)
                if icon_path and os.path.exists(icon_path):
                    pixmap = QPixmap(icon_path)
                    avatar_label.setPixmap(pixmap.scaled(40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                    avatar_label.setStyleSheet("""
                        QLabel {
                            border: 1px solid #ccc;
                            border-radius: 20px;
                            padding: 2px;
                        }
                    """)
                else:
                    # Если нет аватара, показываем первую букву названия команды
                    avatar_label.setText(name[0].upper())
                    avatar_label.setAlignment(Qt.AlignCenter)
                    avatar_label.setStyleSheet("""
                        QLabel {
                            background-color: #4CAF50;
                            color: white;
                            border-radius: 20px;
                            font-size: 18px;
                            font-weight: bold;
                        }
                    """)
                
                # Информация о команде
                info_layout = QVBoxLayout()
                name_label = QLabel(f"{name}")
                name_label.setStyleSheet("font-weight: bold; font-size: 14px;")
                role_label = QLabel(f"Роль: {role}")
                role_label.setStyleSheet("color: #666; font-size: 12px;")
                info_layout.addWidget(name_label)
                info_layout.addWidget(role_label)
                
                item_layout.addWidget(avatar_label)
                item_layout.addLayout(info_layout)
                item_layout.addStretch()
                
                # Создаем элемент списка
                item = QListWidgetItem()
                item.setData(Qt.UserRole, team_id)  # Сохраняем ID команды
                item.setData(Qt.UserRole + 1, name)  # Сохраняем имя команды
                item.setSizeHint(item_widget.sizeHint())
                
                teams_list.addItem(item)
                teams_list.setItemWidget(item, item_widget)
            
            # Обновляем обработчик клика
            def on_team_click(item):
                team_id = item.data(Qt.UserRole)
                team_name = item.data(Qt.UserRole + 1)
                self.teams_dialog.close()
                # Используем QTimer вместо after
                QTimer.singleShot(100, lambda: self.show_team_dialog(team_id, team_name))
            
            teams_list.itemClicked.connect(on_team_click)
            
            # Стилизация списка
            teams_list.setStyleSheet("""
                QListWidget {
                    border: 1px solid #ccc;
                    border-radius: 5px;
                    padding: 5px;
                }
                QListWidget::item {
                    border-bottom: 1px solid #eee;
                    padding: 5px;
                }
                QListWidget::item:hover {
                    background-color: #f5f5f5;
                }
                QListWidget::item:selected {
                    background-color: #e3f2fd;
                    color: black;
                }
            """)
            
            layout.addWidget(teams_list)
        else:
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
        
        self.teams_dialog.setLayout(layout)
        self.teams_dialog.show()

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
            
        if not self.window.current_project_id:
            QMessageBox.warning(self.window, "Ошибка", "Сначала выберите проект")
            return
            
        # Получаем информацию о текущем проекте
        project_info = self.db.get_project_info(self.window.current_project_id)
        if not project_info:
            QMessageBox.warning(self.window, "Ошибка", "Ошибка получения информации о проекте")
            return
            
        dlg = QDialog(self.window)
        dlg.setWindowTitle(f"Создание задачи в проекте: {project_info['name']}")
        dlg.resize(500, 400)
        
        layout = QVBoxLayout()
        
        # Название задачи
        title = QLineEdit()
        title.setPlaceholderText("Название задачи")
        layout.addWidget(title)
        
        # Описание
        description = QTextEdit()
        description.setPlaceholderText("Описание задачи")
        layout.addWidget(description)
        
        # Приоритет
        priority_label = QLabel("Приоритет (1-5):")
        layout.addWidget(priority_label)
        priority = QComboBox()
        priority.addItems(['1', '2', '3', '4', '5'])
        layout.addWidget(priority)
        
        # Дедлайн
        deadline_layout = QHBoxLayout()
        deadline_label = QLabel("Дедлайн:")
        deadline_date = QLineEdit()
        deadline_date.setReadOnly(True)
        deadline_time = QTimeEdit()
        deadline_time.setTime(QTime.currentTime())
        
        deadline_layout.addWidget(deadline_label)
        deadline_layout.addWidget(deadline_date)
        deadline_layout.addWidget(deadline_time)
        layout.addLayout(deadline_layout)
        
        calendar = QCalendarWidget()
        calendar.clicked.connect(lambda date: deadline_date.setText(date.toString("dd.MM.yyyy")))
        layout.addWidget(calendar)
        
        # Уведомления
        notification_layout = QHBoxLayout()
        notification_label = QLabel("Уведомить за:")
        notification_preset = QComboBox()
        notification_preset.addItems([
            "В момент дедлайна",
            "5 минут",
            "10 минут",
            "15 минут",
            "30 минут",
            "1 час",
            "Другое..."
        ])
        
        notification_custom = QLineEdit()
        notification_custom.setPlaceholderText("минут")
        notification_custom.setVisible(False)
        
        def on_notification_changed(text):
            notification_custom.setVisible(text == "Другое...")
        
        notification_preset.currentTextChanged.connect(on_notification_changed)
        
        notification_layout.addWidget(notification_label)
        notification_layout.addWidget(notification_preset)
        notification_layout.addWidget(notification_custom)
        
        layout.addLayout(notification_layout)
        
        # Кнопка создания
        button_layout = QHBoxLayout()
        create_button = QPushButton("Создать задачу")
        create_button.setStyleSheet(self.window.style_button())
        button_layout.addWidget(create_button)
        
        def on_create_button_clicked():
            if not title.text():
                QMessageBox.warning(dlg, "Ошибка", "Введите название задачи")
                return
            
            if not deadline_date.text():
                QMessageBox.warning(dlg, "Ошибка", "Выберите дату дедлайна")
                return
            
            try:
                deadline_str = f"{deadline_date.text()} {deadline_time.time().toString('HH:mm')}"
                deadline_datetime = datetime.strptime(deadline_str, "%d.%m.%Y %H:%M")
                
                notification_preset_text = notification_preset.currentText()
                if notification_preset_text == "В момент дедлайна":
                    notification_time = deadline_datetime
                elif notification_preset_text == "Другое...":
                    try:
                        minutes = int(notification_custom.text())
                        notification_time = deadline_datetime - timedelta(minutes=minutes)
                    except ValueError:
                        QMessageBox.warning(dlg, "Ошибка", "Введите корректное количество минут")
                        return
                else:
                    time_map = {
                        "5 минут": 5,
                        "10 минут": 10,
                        "15 минут": 15,
                        "30 минут": 30,
                        "1 час": 60
                    }
                    minutes = time_map.get(notification_preset_text, 0)
                    notification_time = deadline_datetime - timedelta(minutes=minutes)
                
                # Отладочный вывод параметров задачи
                print("=== Создание новой задачи ===")
                print(f"Название: {title.text()}")
                print(f"Описание: {description.toPlainText()}")
                print(f"ID пользователя: {self.current_user['user_id']}")
                print(f"Дедлайн: {deadline_datetime}")
                print(f"Приоритет: {priority.currentText()}")
                print(f"ID проекта: {self.window.current_project_id}")
                print(f"ID команды: {project_info['team_id']}")
                print(f"Время уведомления: {notification_time}")
                print(f"Время создания: {datetime.now()}")
                
                task = Task(
                    title=title.text(),
                    description=description.toPlainText(),
                    user_id=self.current_user['user_id'],
                    status=False,
                    deadline=deadline_datetime,
                    priority=int(priority.currentText()),
                    project_id=self.window.current_project_id,
                    team_id=project_info['team_id'],
                    notification_time=notification_time,
                    notified=False,
                    created_at=datetime.now()
                )
                
                # Отладочный вывод объекта задачи
                print("\n=== Объект Task ===")
                print(f"Атрибуты задачи: {task.__dict__}")
                
                task_id = self.db.add_task(task)
                if task_id:
                    print(f"\nЗадача успешно создана с ID: {task_id}")
                    QMessageBox.information(dlg, "Успех", "Задача создана успешно!")
                    dlg.accept()
                    # Обновляем отображение задач
                    self.window.display_project_tasks(self.window.current_project_id, project_info['name'])
                else:
                    print("\nОшибка: Не удалось создать задачу")
                    QMessageBox.critical(dlg, "Ошибка", "Не удалось создать задачу")
                
            except Exception as e:
                print(f"\n=== Ошибка при создании задачи ===")
                print(f"Тип ошибки: {type(e).__name__}")
                print(f"Текст ошибки: {str(e)}")
                print(f"Полная информация:")
                import traceback
                traceback.print_exc()
                QMessageBox.critical(dlg, "Ошибка", f"Ошибка при создании задачи: {str(e)}")
        
        create_button.clicked.connect(on_create_button_clicked)
        layout.addLayout(button_layout)
        
        dlg.setLayout(layout)
        dlg.exec()
        
    def validate_email(self, email: str) -> bool:
        """Проверка валидности email"""
        # Паттерн для проверки email
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
        
    def show_login_dialog(self):
        """Показать диалог входа"""
        try:
            self.login_dialog = QDialog(self.window)
            self.login_dialog.setWindowTitle("Вход")
            layout = QVBoxLayout()

            # Email
            email_label = QLabel("Email:")
            self.email_edit = QLineEdit()
            layout.addWidget(email_label)
            layout.addWidget(self.email_edit)

            # Пароль
            password_label = QLabel("Пароль:")
            self.password_edit = QLineEdit()
            self.password_edit.setEchoMode(QLineEdit.Password)
            layout.addWidget(password_label)
            layout.addWidget(self.password_edit)

            # Кнопки
            buttons_layout = QHBoxLayout()
            
            login_button = QPushButton("Войти")
            login_button.clicked.connect(self.handle_login)
            
            register_button = QPushButton("Регистрация")
            register_button.clicked.connect(self.show_register_dialog)
            
            buttons_layout.addWidget(login_button)
            buttons_layout.addWidget(register_button)
            layout.addLayout(buttons_layout)

            self.login_dialog.setLayout(layout)
            result = self.login_dialog.exec_()
            
            # Если авторизация успешна, показываем канбан доску
            if result == QDialog.Accepted and self.is_authenticated():
                print("Авторизация успешна, показываем канбан доску")
                self.window.click_input_button()
            
        except Exception as e:
            print(f"Ошибка при создании диалога входа: {e}")
            import traceback
            traceback.print_exc()

    def handle_login(self):
        """Обработчик нажатия кнопки входа"""
        try:
            email = self.email_edit.text()
            password = self.password_edit.text()
            
            if self.login_user(email, password):
                self.login_dialog.accept()
            
        except Exception as e:
            print(f"Ошибка при обработке входа: {e}")
            import traceback
            traceback.print_exc()

    def show_register_window(self, parent_dialog=None):
        """Показать окно регистрации"""
        dlg = QDialog(self.window)
        dlg.setWindowTitle("Регистрация")
        layout = QVBoxLayout()
        
        # Имя пользователя
        username_edit = QLineEdit()
        username_edit.setPlaceholderText("Имя пользователя")
        layout.addWidget(username_edit)
        
        # Email
        email_edit = QLineEdit()
        email_edit.setPlaceholderText("Email")
        layout.addWidget(email_edit)
        
        # Пароль
        password_edit = QLineEdit()
        password_edit.setPlaceholderText("Пароль")
        password_edit.setEchoMode(QLineEdit.Password)
        layout.addWidget(password_edit)
        
        # Кнопка регистрации
        register_btn = QPushButton("Зарегистрироваться")
        register_btn.setStyleSheet(self.window.style_button())
        
        def try_register():
            if not username_edit.text() or not email_edit.text() or not password_edit.text():
                QMessageBox.warning(dlg, "Ошибка", "Заполните все поля")
                return
            
            try:
                if self.db.check_email_exists(email_edit.text()):
                    QMessageBox.warning(dlg, "Ошибка", "Пользователь с таким email уже существует")
                    return
                    
                user_data = self.db.register_user(
                    username_edit.text(),
                    email_edit.text(),
                    password_edit.text()
                )
                
                if user_data:
                    QMessageBox.information(dlg, "Успех", "Регистрация успешна!")
                    dlg.accept()
                    if parent_dialog:
                        parent_dialog.accept()
                else:
                    QMessageBox.warning(dlg, "Ошибка", "Не удалось зарегистрироваться")
            except Exception as e:
                QMessageBox.critical(dlg, "Ошибка", f"Ошибка при регистрации: {str(e)}")
        
        register_btn.clicked.connect(try_register)
        layout.addWidget(register_btn)
        
        dlg.setLayout(layout)
        dlg.exec_()
        
    def create_team_dialog(self):
        """Диалог создания команды"""
        if not self.is_authenticated():
            QMessageBox.warning(self.window, "Ошибка", "Необходимо войти в систему")
            return
        
        dlg = QDialog(self.window)
        dlg.setWindowTitle("Создание команды")
        layout = QVBoxLayout()
        
        # Название команды
        name_edit = QLineEdit()
        name_edit.setPlaceholderText("Название команды")
        layout.addWidget(name_edit)
        
        # Описание команды
        desc_edit = QTextEdit()
        desc_edit.setPlaceholderText("Описание команды")
        layout.addWidget(desc_edit)
        
        # Аватар команды
        avatar_layout = QHBoxLayout()
        # Определяем avatar_path в правильной области видимости
        avatar_path = [""]  # Используем список для возможности изменения из вложенных функций
        
        avatar_preview = QLabel()
        avatar_preview.setFixedSize(100, 100)
        avatar_preview.setStyleSheet("border: 1px solid #ccc;")
        avatar_preview.setAlignment(Qt.AlignCenter)
        avatar_preview.setText("Нет аватара")
        
        def select_avatar():
            file_name, _ = QFileDialog.getOpenFileName(
                dlg,
                "Выберите аватар команды",
                "",
                "Изображения (*.png *.jpg *.jpeg)"
            )
            if file_name:
                try:
                    # Проверяем и обрабатываем изображение
                    with Image.open(file_name) as img:
                        # Конвертируем в RGB если изображение в другом формате
                        if img.mode != 'RGB':
                            img = img.convert('RGB')
                        # Создаем миниатюру
                        img.thumbnail((100, 100))
                        # Сохраняем путь
                        avatar_path[0] = file_name
                        # Показываем превью
                        pixmap = QPixmap(file_name)
                        avatar_preview.setPixmap(pixmap.scaled(100, 100, Qt.KeepAspectRatio))
                except Exception as e:
                    QMessageBox.warning(dlg, "Ошибка", f"Ошибка при загрузке изображения: {str(e)}")
        
        def clear_avatar():
            avatar_path[0] = ""
            avatar_preview.setText("Нет аватара")
            avatar_preview.setPixmap(QPixmap())
        
        select_avatar_btn = QPushButton("Выбрать аватар")
        clear_avatar_btn = QPushButton("Убрать аватар")
        select_avatar_btn.clicked.connect(select_avatar)
        clear_avatar_btn.clicked.connect(clear_avatar)
        
        avatar_layout.addWidget(avatar_preview)
        avatar_buttons = QVBoxLayout()
        avatar_buttons.addWidget(select_avatar_btn)
        avatar_buttons.addWidget(clear_avatar_btn)
        avatar_layout.addLayout(avatar_buttons)
        layout.addLayout(avatar_layout)
        
        # Кнопки создания/отмены
        buttons_layout = QHBoxLayout()
        create_btn = QPushButton("Создать")
        cancel_btn = QPushButton("Отмена")
        create_btn.setStyleSheet(self.window.style_button())
        cancel_btn.setStyleSheet(self.window.style_button())
        
        def try_create_team():
            if not name_edit.text():
                QMessageBox.warning(dlg, "Ошибка", "Введите название команды")
                return
            
            try:
                print("\n=== Создание команды ===")
                print(f"Текущий пользователь: {self.current_user}")
                print(f"Название команды: {name_edit.text()}")
                print(f"Описание: {desc_edit.toPlainText()}")
                print(f"Путь к аватару: {avatar_path[0]}")
                
                # Сохраняем аватар если он был выбран
                final_avatar_path = None
                if avatar_path[0]:
                    try:
                        avatar_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "team_avatars")
                        print(f"Директория для аватаров: {avatar_dir}")
                        
                        if not os.path.exists(avatar_dir):
                            os.makedirs(avatar_dir)
                            print("Создана директория для аватаров")
                        
                        extension = os.path.splitext(avatar_path[0])[1]
                        final_avatar_path = os.path.join(
                            avatar_dir, 
                            f"team_avatar_{datetime.now().strftime('%Y%m%d_%H%M%S')}{extension}"
                        )
                        print(f"Путь сохранения аватара: {final_avatar_path}")
                        
                        shutil.copy2(avatar_path[0], final_avatar_path)
                        print("Аватар успешно скопирован")
                    except Exception as avatar_error:
                        print(f"Ошибка при сохранении аватара: {avatar_error}")
                        final_avatar_path = None
                
                team_id = self.db.create_team(
                    name_edit.text(),
                    desc_edit.toPlainText(),
                    self.current_user['user_id'],
                    final_avatar_path
                )
                
                if team_id:
                    QMessageBox.information(dlg, "Успех", "Команда успешно создана!")
                    dlg.accept()
                    # Обновляем список команд
                    self.click_teams_button()
                else:
                    QMessageBox.warning(dlg, "Ошибка", "Не удалось создать команду")
                    
            except Exception as e:
                print(f"Ошибка при создании команды: {e}")
                import traceback
                traceback.print_exc()
                QMessageBox.critical(dlg, "Ошибка", f"Ошибка при создании команды: {str(e)}")
        
        create_btn.clicked.connect(try_create_team)
        cancel_btn.clicked.connect(dlg.reject)
        
        buttons_layout.addWidget(create_btn)
        buttons_layout.addWidget(cancel_btn)
        layout.addLayout(buttons_layout)
        
        dlg.setLayout(layout)
        dlg.exec_()

    def on_team_selected(self, team_id: int, team_name: str):
        """Обработка выбора команды"""
        print(f"Выбрана команда: {team_name} (ID: {team_id})")
        self.show_team_dialog(team_id, team_name)

    def update_team_dialog_content(self, team_id: int, team_name: str):
        """Обновление содержимого диалога команды"""
        if hasattr(self, 'team_dialog') and self.team_dialog is not None:
            # Обновляем список проектов
            projects = self.db.get_team_projects(team_id)
            if hasattr(self, 'projects_list'):
                self.projects_list.clear()
                if projects:
                    for project in projects:
                        project_id, name, description, created_at = project
                        item = QListWidgetItem(f"{name}")
                        if description:
                            item.setToolTip(description)
                        item.setData(Qt.UserRole, project_id)
                        item.setData(Qt.UserRole + 1, name)
                        self.projects_list.addItem(item)

    def show_team_dialog(self, team_id: int, team_name: str):
        """Показ диалога команды"""
        if hasattr(self, 'team_dialog') and self.team_dialog is not None:
            self.team_dialog.close()
        
        print(f"Открываем диалог команды: {team_name}")
        
        self.team_dialog = QDialog(self.window)
        self.team_dialog.setWindowTitle(f"Команда: {team_name}")
        self.team_dialog.resize(600, 400)
        
        layout = QVBoxLayout()
        
        # Верхняя панель с кнопками управления командой
        top_panel = QHBoxLayout()
        
        # Кнопка приглашения участников
        invite_btn = QPushButton("Пригласить участника")
        invite_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        invite_btn.clicked.connect(lambda: self.show_invite_dialog(team_id))
        top_panel.addWidget(invite_btn)
        
        # Добавляем растягивающийся элемент для выравнивания
        top_panel.addStretch()
        
        layout.addLayout(top_panel)
        
        # Список проектов
        projects_label = QLabel("Проекты команды:")
        projects_label.setStyleSheet("font-weight: bold; font-size: 14px; margin: 10px 0;")
        layout.addWidget(projects_label)
        
        projects = self.db.get_team_projects(team_id)
        print(f"Получено проектов: {len(projects)}")
        
        if projects:
            self.projects_list = QListWidget()
            for project in projects:
                project_id, name, description, created_at = project
                item = QListWidgetItem(f"{name}")
                if description:
                    item.setToolTip(description)
                item.setData(Qt.UserRole, project_id)
                item.setData(Qt.UserRole + 1, name)
                self.projects_list.addItem(item)
            
            def on_project_click(item):
                project_id = item.data(Qt.UserRole)
                project_name = item.data(Qt.UserRole + 1)
                self.team_dialog.close()
                self.on_project_selected(project_id, project_name)
            
            self.projects_list.itemClicked.connect(on_project_click)
            layout.addWidget(self.projects_list)
        else:
            no_projects_label = QLabel("В команде пока нет проектов")
            no_projects_label.setAlignment(Qt.AlignCenter)
            no_projects_label.setStyleSheet("color: #666; padding: 20px;")
            layout.addWidget(no_projects_label)
        
        # Кнопка создания проекта
        create_project_btn = QPushButton("Создать проект")
        create_project_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                margin-top: 10px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        create_project_btn.clicked.connect(lambda: self.show_create_project_dialog(team_id))
        layout.addWidget(create_project_btn)
        
        self.team_dialog.setLayout(layout)
        self.team_dialog.exec_()

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
                project_id = self.db.create_project(name_edit.text(), desc_edit.toPlainText(), team_id)
                if project_id:
                    QMessageBox.information(dlg, "Успех", "Проект успешно создан!")
                    dlg.accept()
                    
                    # Обновляем список проектов, вызывая on_team_selected
                    team_name = self.db.get_team_name(team_id)  # Нужно добавить этот метод в Database
                    if team_name:
                        self.on_team_selected(team_id, team_name)
                else:
                    QMessageBox.warning(dlg, "Ошибка", "Не удалось создать проект")
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
        
        # Иконка добавления пользователя
        icon_label = QLabel()
        icon_path = "icons/add_user.png"
        if os.path.exists(icon_path):
            icon_pixmap = QPixmap(icon_path)
        else:
            # Если иконка не найдена, используем текст
            icon_label.setText("➕👤")
            icon_label.setStyleSheet("font-size: 24px;")
        icon_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(icon_label)
        
        email_edit = QLineEdit()
        email_edit.setPlaceholderText("Email пользователя")
        layout.addWidget(email_edit)
        
        invite_btn = QPushButton("Пригласить")
        invite_btn.setStyleSheet(self.window.style_button())
        if os.path.exists(icon_path):
            invite_btn.setIcon(QIcon(icon_path))
        
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

    def on_project_selected(self, project_id, project_name):
        """Обработка выбора проекта"""
        self.window.current_project_id = project_id  # Сохраняем ID текущего проекта
        self.window.display_project_tasks(project_id, project_name)

    def login_user(self, email: str, password: str):
        """Авторизация пользователя"""
        try:
            user_data = self.db.login_user(email, password)
            if user_data:
                self.current_user = {
                    'user_id': user_data[0],
                    'username': user_data[1],
                    'email': user_data[2],
                    'created_at': user_data[3]
                }
                self.window.update_user_panel()
                
                # Закрываем окно авторизации
                if hasattr(self, 'login_dialog'):
                    self.login_dialog.accept()
                    
                # После успешной авторизации показываем канбан доску
                QTimer.singleShot(100, self.window.click_input_button)
                
                return True
            else:
                QMessageBox.warning(
                    self.window,
                    "Ошибка",
                    "Неверный email или пароль"
                )
                return False
        except Exception as e:
            QMessageBox.critical(
                self.window,
                "Ошибка",
                f"Ошибка при входе: {str(e)}"
            )
            return False

    def show_register_dialog(self):
        """Показать диалог регистрации"""
        try:
            register_dialog = QDialog(self.window)
            register_dialog.setWindowTitle("Регистрация")
            layout = QVBoxLayout()

            # Имя пользователя
            username_label = QLabel("Имя пользователя:")
            username_edit = QLineEdit()
            layout.addWidget(username_label)
            layout.addWidget(username_edit)

            # Email
            email_label = QLabel("Email:")
            email_edit = QLineEdit()
            layout.addWidget(email_label)
            layout.addWidget(email_edit)

            # Пароль
            password_label = QLabel("Пароль:")
            password_edit = QLineEdit()
            password_edit.setEchoMode(QLineEdit.Password)
            layout.addWidget(password_label)
            layout.addWidget(password_edit)

            # Подтверждение пароля
            confirm_password_label = QLabel("Подтвердите пароль:")
            confirm_password_edit = QLineEdit()
            confirm_password_edit.setEchoMode(QLineEdit.Password)
            layout.addWidget(confirm_password_label)
            layout.addWidget(confirm_password_edit)

            # Кнопка регистрации
            register_button = QPushButton("Зарегистрироваться")
            
            def handle_register():
                username = username_edit.text()
                email = email_edit.text()
                password = password_edit.text()
                confirm_password = confirm_password_edit.text()
                
                if not all([username, email, password, confirm_password]):
                    QMessageBox.warning(register_dialog, "Ошибка", "Все поля должны быть заполнены")
                    return
                    
                if password != confirm_password:
                    QMessageBox.warning(register_dialog, "Ошибка", "Пароли не совпадают")
                    return
                    
                try:
                    if self.db.register_user(username, email, password):
                        QMessageBox.information(register_dialog, "Успех", "Регистрация успешно завершена")
                        register_dialog.accept()
                    else:
                        QMessageBox.warning(register_dialog, "Ошибка", "Не удалось зарегистрировать пользователя")
                except Exception as e:
                    QMessageBox.critical(register_dialog, "Ошибка", f"Ошибка при регистрации: {str(e)}")
            
            register_button.clicked.connect(handle_register)
            layout.addWidget(register_button)

            register_dialog.setLayout(layout)
            register_dialog.exec_()
            
        except Exception as e:
            print(f"Ошибка при создании диалога регистрации: {e}")
            import traceback
            traceback.print_exc()



#TODO: 1. Сделать атворизацию пользователя и чтобы совершать действия от его лица (комментарии, созбании проетков, создание задач)        
#TODO  2. Сделать создание задач (использование иконок, для записи в календарь, запись приоритета с помощью SelectBox, Дата дедлайна, напомининие поставить по дефолту как задача сейчас по времени в тот момент и уведомлять)
#TODO  3. сделать вывод проектов и возомжно по ним нажимать и редактировать как в было в прошлой итерации
#TODO  4. Сделать историю где будет написаны изменения и написано кто внес изменения.

#На данный момент реализована регистрация с записью в бд SadSmile