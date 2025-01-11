import os
from PyQt5.QtWidgets import (QMainWindow, QPushButton, QVBoxLayout, QDialog, 
                            QLabel, QFrame, QApplication, QScrollArea, QWidget, QMessageBox, QHBoxLayout, QLineEdit, QTextEdit, QListWidget, QSizePolicy, QDateTimeEdit, QSpinBox)
from PyQt5.QtCore import Qt, QDateTime
from PyQt5.QtGui import QIcon, QPixmap
from functionality import Functionality
from Task import Task
from PIL import Image
from Team import Team
from datetime import datetime
from datetime import datetime, timedelta
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QPushButton, QLabel, QScrollArea)
from PyQt5.QtCore import Qt
from functionality import Functionality
import os
from kanban_board import KanbanBoard
from dialogs import CreateTaskDialog  # Добавляем импорт

class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Система управления задачами")
        
        # Инициализируем Functionality
        
        self.func = Functionality(self)
        
        # Создаем центральный виджет и главный layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        
        # Создаем левую панель
        left_panel = QVBoxLayout()
        
        # Добавляем панель пользователя
        self.create_user_panel()
        left_panel.addWidget(self.user_panel)
        
        # Добавляем кнопку выбора команды
        self.select_team_button = QPushButton("Выбрать команду")
        self.select_team_button.setStyleSheet("""
            QPushButton {
                background-color: #f0f0f0;
                border: none;
                padding: 8px;
                border-radius: 4px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
        """)
        self.select_team_button.clicked.connect(self.func.click_teams_button)
        left_panel.addWidget(self.select_team_button)
        
        # Добавляем кнопки навигации
        nav_buttons = QVBoxLayout()
        self.create_nav_buttons(nav_buttons)
        left_panel.addLayout(nav_buttons)
        
        # Создаем кнопку задач для нижней панели
        self.task_button = QPushButton("Задачи")
        self.task_button.setStyleSheet("""
            QPushButton {
                background-color: #f0f0f0;
                border: none;
                padding: 8px;
                border-radius: 4px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
        """)
        self.task_button.clicked.connect(self.click_input_button)
        
        # Добавляем растягивающийся элемент
        left_panel.addStretch()
        
        # Создаем нижнюю панель
        bottom_panel = QHBoxLayout()
        bottom_panel.addWidget(self.task_button)
        left_panel.addLayout(bottom_panel)
        
        # Добавляем левую панель в главный layout
        main_layout.addLayout(left_panel)
        
        # Создаем правую панель
        right_panel = QVBoxLayout()
        
        # Добавляем заголовок
        self.title_label = QLabel("Добро пожаловать!")
        self.title_label.setStyleSheet("""
            QLabel {
                font-size: 24px;
                margin: 20px 0;
            }
        """)
        right_panel.addWidget(self.title_label)
        
        # Добавляем layout для задач
        self.tasks_layout = QVBoxLayout()
        right_panel.addLayout(self.tasks_layout)
        
        # Добавляем правую панель в главный layout
        main_layout.addLayout(right_panel, stretch=1)
        
        # Создаем кнопку добавления задачи
        self.create_task_button()
        
        # Устанавливаем размер окна
        self.resize(1200, 800)

    def create_nav_buttons(self, layout):
        """Создание кнопок навигации"""
        # Кнопка "Входящие"
        self.input_button = QPushButton("Входящие")
        self.input_button.setStyleSheet("""
            QPushButton {
                background-color: #f0f0f0;
                border: none;
                padding: 8px;
                border-radius: 4px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
        """)
        self.input_button.clicked.connect(self.click_input_button)
        layout.addWidget(self.input_button)
        
        # Кнопка "Проекты"
        self.projects_button = QPushButton("Проекты")
        self.projects_button.setStyleSheet("""
            QPushButton {
                background-color: #f0f0f0;
                border: none;
                padding: 8px;
                border-radius: 4px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
        """)
        self.projects_button.clicked.connect(self.click_projects_button)
        layout.addWidget(self.projects_button)

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
        """Создание кнопки добавления задачи"""
        self.add_task_button = QPushButton("+", self)
        self.add_task_button.setFixedSize(50, 50)
        self.add_task_button.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border-radius: 25px;
                font-size: 24px;
                font-weight: bold;
                border: none;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        
        # Позиционируем кнопку в правом нижнем углу
        self.add_task_button.move(
            self.width() - self.add_task_button.width() - 20,
            self.height() - self.add_task_button.height() - 20
        )
        
        self.add_task_button.clicked.connect(self.show_create_task_dialog)

    def show_create_task_dialog(self):
        """Показать диалог создания задачи"""
        if not self.func.is_authenticated():
            QMessageBox.warning(self, "Ошибка", "Необходимо войти в систему")
            return
        
        try:
            dialog = CreateTaskDialog(
                parent=self,
                db=self.func.db,
                current_user=self.func.current_user
            )
            
            if dialog.exec_() == QDialog.Accepted:
                data = dialog.get_data()
                new_task = Task(
                    title=data['title'],
                    description=data['description'],
                    user_id=self.func.current_user['user_id'],
                    status=0,  # 0 - не начато
                    deadline=data['deadline'],
                    created_at=datetime.now(),
                    team_id=data['team_id'],
                    project_id=data['project_id'],
                    priority=data['priority']
                )
                
                if self.func.db.create_task(new_task):
                    self.click_input_button()  # Обновляем канбан доску
                    QMessageBox.information(self, "Успех", "Задача создана")
                else:
                    QMessageBox.critical(self, "Ошибка", "Не удалось создать задачу")
                
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось создать задачу: {str(e)}")

    def resizeEvent(self, event):
        """Обработчик изменения размера окна"""
        super().resizeEvent(event)
        if hasattr(self, 'add_task_button'):
            # Обновляем позицию кнопки при изменении размера окна
            self.add_task_button.move(
                self.width() - self.add_task_button.width() - 20,
                self.height() - self.add_task_button.height() - 20
            )

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
        """Создание панели пользователя"""
        self.user_panel = QFrame()
        self.user_panel.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 5px;
                margin: 5px;
                padding: 10px;
            }
        """)
        
        user_layout = QVBoxLayout(self.user_panel)
        
        # Иконка пользователя
        icon_label = QLabel()
        icon_path = "icons_team/user.pnjyb g"
        
        # Проверяем существование файла иконки
        if os.path.exists(icon_path):
            icon_pixmap = QPixmap(icon_path)
            if not icon_pixmap.isNull():
                icon_pixmap = icon_pixmap.scaled(48, 48, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                icon_label.setPixmap(icon_pixmap)
        else:
            print(f"Иконка не найдена: {icon_path}")
            icon_label.setText("👤")
            icon_label.setStyleSheet("""
                QLabel {
                    font-size: 32px;
                    color: #666;
                }
            """)
        
        icon_label.setAlignment(Qt.AlignCenter)
        user_layout.addWidget(icon_label)
        
        # Метка для отображения имени пользователя
        self.user_label = QLabel("Гость")
        self.user_label.setStyleSheet("""
            QLabel {
                color: #333;
                font-size: 14px;
                font-weight: bold;
                padding: 5px;
            }
        """)
        self.user_label.setAlignment(Qt.AlignCenter)
        user_layout.addWidget(self.user_label)
        
        # Метка для отображения email
        self.email_label = QLabel("")
        self.email_label.setStyleSheet("""
            QLabel {
                color: #666;
                font-size: 12px;
                padding: 2px;
            }
        """)
        self.email_label.setAlignment(Qt.AlignCenter)
        user_layout.addWidget(self.email_label)
        
        # Разделительная линия
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setStyleSheet("background-color: #ddd;")
        user_layout.addWidget(line)
        
        # Кнопка входа/выхода
        self.login_button = QPushButton("Войти")
        self.login_button.setStyleSheet(self.style_button())
        self.login_button.clicked.connect(self.handle_auth)
        user_layout.addWidget(self.login_button)
        
        user_layout.addStretch()

    def update_user_panel(self):
        """Обновление панели пользователя"""
        if self.func.is_authenticated():
            # Обновляем информацию о пользователе
            user = self.func.get_current_user()
            self.user_label.setText(user['username'])
            self.email_label.setText(user['email'])
            self.email_label.setVisible(True)
            
            # Обновляем кнопку
            self.login_button.setText("Выйти")
            try:
                self.login_button.clicked.disconnect()
            except:
                pass
            self.login_button.clicked.connect(self.handle_logout)
        else:
            # Сбрасываем на состояние "гость"
            self.user_label.setText("Гость")
            self.email_label.setText("")
            self.email_label.setVisible(False)
            
            # Обновляем кнопку
            self.login_button.setText("Войти")
            try:
                self.login_button.clicked.disconnect()
            except:
                pass
            self.login_button.clicked.connect(self.handle_auth)

    def handle_auth(self):
        """Обработчик нажатия кнопки авторизации"""
        try:
            if self.func.is_authenticated():
                # Если пользователь уже авторизован - выходим
                self.func.logout()
                self.update_user_panel()
            else:
                # Если не авторизован - показываем окно входа
                self.func.show_login_dialog()  # Исправлено с show_login_window на show_login_dialog
        except Exception as e:
            print(f"Ошибка при обработке авторизации: {e}")
            import traceback
            traceback.print_exc()

    def handle_logout(self):
        """Обработка выхода из системы"""
        try:
            self.func.logout()
            self.update_user_panel()
            # Очищаем список задач при выходе
            for i in reversed(range(self.tasks_layout.count())): 
                widget = self.tasks_layout.itemAt(i).widget()
                if widget is not None:
                    widget.deleteLater()
            # Сбрасываем заголовок
            self.title_label.setText("Мои задачи")
        except Exception as e:
            print(f"Ошибка при выходе: {str(e)}")
            import traceback
            traceback.print_exc()

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

    def display_project_tasks(self, project_id, project_name):
        """Отображение задач проекта"""
        print(f"\n=== Отображение задач для проекта {project_name} (ID: {project_id}) ===")
        
        # Очищаем текущий layout
        for i in reversed(range(self.tasks_layout.count())): 
            widget = self.tasks_layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()
        
        # Обновляем заголовок
        self.title_label.setText(f"Задачи проекта: {project_name}")
        
        # Получаем задачи проекта
        tasks = self.func.db.get_project_tasks(project_id)
        print(f"Получено задач: {len(tasks)}")
        
        if tasks:
            print("Начинаем отображение задач")
            for task in tasks:
                print(f"\nОтображение задачи: {task.title}")
                task_widget = QFrame()
                task_widget.setStyleSheet("""
                    QFrame {
                        background-color: white;
                        border: 1px solid #ddd;
                        border-radius: 5px;
                        margin: 5px;
                        padding: 10px;
                    }
                """)
                
                task_layout = QVBoxLayout(task_widget)
                
                # Название задачи
                task_name = QLabel(task.title)
                task_name.setStyleSheet("font-weight: bold;")
                task_layout.addWidget(task_name)
                
                # Описание задачи
                if task.description:
                    task_desc = QLabel(task.description)
                    task_layout.addWidget(task_desc)
                
                # Дедлайн
                if task.deadline:
                    deadline_label = QLabel(f"Дедлайн: {task.deadline}")
                    task_layout.addWidget(deadline_label)
                
                self.tasks_layout.addWidget(task_widget)
                print(f"Задача {task.title} добавлена в layout")
        else:
            print("Задач не найдено, отображаем сообщение")
            # Если задач нет, показываем сообщение
            no_tasks_label = QLabel("В этом проекте пока нет задач")
            no_tasks_label.setAlignment(Qt.AlignCenter)
            no_tasks_label.setStyleSheet("""
                QLabel {
                    color: #666;
                    padding: 20px;
                    font-size: 14px;
                }
            """)
            self.tasks_layout.addWidget(no_tasks_label)
        
        # Добавляем растягивающийся элемент в конец
        self.tasks_layout.addStretch()
        print("=== Завершено отображение задач ===\n")

    def update_select_team_button(self):
        """Обновление кнопки выбора команды"""
        if hasattr(self, 'select_team_button'):
            if self.func.is_authenticated() and self.func.get_current_team():
                team = self.func.get_current_team()
                self.select_team_button.setText(f"Команда: {team['name']}")
            else:
                self.select_team_button.setText("Выбрать команду")

    def clear_team_photo(self):
        # Очищаем путь к фото
        self.team_photo_path = ""
        # Очищаем предпросмотр фото (если есть)
        self.photo_preview_label.clear()
        # Можно установить текст по умолчанию или иконку
        self.photo_preview_label.setText("Фото не выбрано")

    def click_input_button(self):
        """Показать канбан доску со всеми задачами"""
        print("\n=== Отображение канбан доски ===")
        
        if not self.func.is_authenticated():
            print("Пользователь не авторизован")
            QMessageBox.warning(self, "Ошибка", "Необходимо войти в систему")
            return
        
        print(f"Текущий пользователь: {self.func.current_user}")
        
        try:
            # Очищаем текущий layout задач
            for i in reversed(range(self.tasks_layout.count())): 
                widget = self.tasks_layout.itemAt(i).widget()
                if widget is not None:
                    widget.deleteLater()
            
            # Обновляем заголовок
            self.title_label.setText("Мои задачи")
            
            # Создаем канбан доску
            print("Создание канбан доски")
            kanban = KanbanBoard()
            kanban.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            
            # Получаем задачи пользователя из базы данных
            tasks = self.func.db.get_user_tasks(self.func.current_user['user_id'])
            print(f"Получено задач: {len(tasks)}")
            
            # Распределяем задачи по колонкам
            for task in tasks:
                print(f"Добавление задачи: {task.title} (Статус: {task.status}, Приоритет: {task.priority})")
                if task.status == True:
                    kanban.add_task(task, "completed")
                else:
                    if task.priority <= 2:
                        kanban.add_task(task, "backlog")
                    else:
                        kanban.add_task(task, "new")
            
            # Добавляем канбан доску в layout
            print("Добавление канбан доски в layout")
            self.tasks_layout.addWidget(kanban)
            
            print("=== Завершено отображение канбан доски ===\n")
            
        except Exception as e:
            print(f"Ошибка при отображении канбан доски: {e}")
            import traceback
            traceback.print_exc()

    def click_projects_button(self):
        """Обработчик нажатия кнопки Проекты"""
        if not self.func.is_authenticated():
            QMessageBox.warning(self, "Ошибка", "Необходимо войти в систему")
            return
        
        # Очищаем текущий layout задач
        for i in reversed(range(self.tasks_layout.count())): 
            widget = self.tasks_layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()
        
        # Обновляем заголовок
        self.title_label.setText("Проекты")
        
        # Здесь будет код для отображения проектов
        # Пока оставим заглушку
        placeholder = QLabel("Здесь будет список проектов")
        placeholder.setStyleSheet("""
            QLabel {
                color: #666;
                font-size: 14px;
                padding: 20px;
            }
        """)
        self.tasks_layout.addWidget(placeholder)
        self.tasks_layout.addStretch()

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
