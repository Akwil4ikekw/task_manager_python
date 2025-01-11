from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                            QLineEdit, QTextEdit, QPushButton, QComboBox, 
                            QCalendarWidget, QTimeEdit, QTabWidget, QListWidget, 
                            QListWidgetItem, QInputDialog, QMessageBox,QWidget, QGroupBox)
from PyQt5.QtCore import Qt, QTime,QDate



from datetime import datetime

class CreateTaskDialog(QDialog):
    def __init__(self, parent=None, db=None, current_user=None):
        super().__init__(parent)
        self.db = db
        self.current_user = current_user
        self.setWindowTitle("Создание новой задачи")
        self.resize(500, 700)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # Группа выбора команды и проекта
        selection_group = QGroupBox("Выбор команды и проекта")
        selection_layout = QVBoxLayout()

        # Выбор команды
        team_label = QLabel("Команда:")
        self.team_combo = QComboBox()
        self.team_combo.setStyleSheet("""
            QComboBox {
                padding: 5px;
                border: 1px solid #ccc;
                border-radius: 3px;
                min-height: 25px;
            }
        """)
        teams = self.db.get_user_teams(self.current_user['user_id'])
        self.team_combo.addItem("Выберите команду", None)
        for team in teams:
            self.team_combo.addItem(team[1], team[0])  # name, id
        selection_layout.addWidget(team_label)
        selection_layout.addWidget(self.team_combo)

        # Выбор проекта
        project_label = QLabel("Проект:")
        self.project_combo = QComboBox()
        self.project_combo.setStyleSheet("""
            QComboBox {
                padding: 5px;
                border: 1px solid #ccc;
                border-radius: 3px;
                min-height: 25px;
            }
        """)
        self.project_combo.addItem("Сначала выберите команду", None)
        selection_layout.addWidget(project_label)
        selection_layout.addWidget(self.project_combo)

        # Обновление списка проектов при выборе команды
        self.team_combo.currentIndexChanged.connect(self.update_projects)

        selection_group.setLayout(selection_layout)
        layout.addWidget(selection_group)

        # Группа основной информации
        task_group = QGroupBox("Информация о задаче")
        task_layout = QVBoxLayout()

        # Название
        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("Введите название задачи")
        task_layout.addWidget(QLabel("Название:"))
        task_layout.addWidget(self.title_edit)

        # Описание
        self.desc_edit = QTextEdit()
        self.desc_edit.setPlaceholderText("Введите описание задачи")
        task_layout.addWidget(QLabel("Описание:"))
        task_layout.addWidget(self.desc_edit)

        # Приоритет
        priority_label = QLabel("Приоритет:")
        self.priority_combo = QComboBox()
        self.priority_combo.addItems([
            "1 - Низкий",
            "2 - Ниже среднего",
            "3 - Средний",
            "4 - Высокий",
            "5 - Критический"
        ])
        self.priority_combo.setCurrentText("3 - Средний")
        task_layout.addWidget(priority_label)
        task_layout.addWidget(self.priority_combo)

        # Группа дедлайна
        deadline_group = QGroupBox("Дедлайн")
        deadline_layout = QVBoxLayout()
        
        self.deadline_calendar = QCalendarWidget()
        self.deadline_calendar.setMinimumDate(QDate.currentDate())
        deadline_layout.addWidget(self.deadline_calendar)
        
        time_layout = QHBoxLayout()
        time_label = QLabel("Время:")
        self.time_edit = QTimeEdit(QTime.currentTime())
        time_layout.addWidget(time_label)
        time_layout.addWidget(self.time_edit)
        deadline_layout.addLayout(time_layout)
        
        deadline_group.setLayout(deadline_layout)
        task_layout.addWidget(deadline_group)

        task_group.setLayout(task_layout)
        layout.addWidget(task_group)

        # Кнопки
        buttons = QHBoxLayout()
        save_btn = QPushButton("Создать")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 8px 16px;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        cancel_btn = QPushButton("Отмена")
        cancel_btn.setStyleSheet("""
            QPushButton {
                padding: 8px 16px;
                border: 1px solid #ccc;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #f0f0f0;
            }
        """)

        save_btn.clicked.connect(self.validate_and_accept)
        cancel_btn.clicked.connect(self.reject)

        buttons.addWidget(save_btn)
        buttons.addWidget(cancel_btn)
        layout.addLayout(buttons)

    def update_projects(self):
        """Обновление списка проектов при выборе команды"""
        self.project_combo.clear()
        team_id = self.team_combo.currentData()
        
        if team_id:
            projects = self.db.get_team_projects(team_id)
            if projects:
                self.project_combo.addItem("Выберите проект", None)
                for project in projects:
                    self.project_combo.addItem(project[1], project[0])  # name, id
            else:
                self.project_combo.addItem("Нет доступных проектов", None)
        else:
            self.project_combo.addItem("Сначала выберите команду", None)

    def validate_and_accept(self):
        """Проверка данных перед принятием"""
        if not self.team_combo.currentData():
            QMessageBox.warning(self, "Ошибка", "Выберите команду")
            return
            
        if not self.project_combo.currentData():
            QMessageBox.warning(self, "Ошибка", "Выберите проект")
            return
            
        if not self.title_edit.text().strip():
            QMessageBox.warning(self, "Ошибка", "Введите название задачи")
            return
            
        self.accept()

    def get_data(self):
        """Получение данных из диалога"""
        priority = int(self.priority_combo.currentText().split()[0])
        return {
            'team_id': self.team_combo.currentData(),
            'project_id': self.project_combo.currentData(),
            'title': self.title_edit.text().strip(),
            'description': self.desc_edit.toPlainText().strip(),
            'priority': priority,
            'deadline': datetime.combine(
                self.deadline_calendar.selectedDate().toPyDate(),
                self.time_edit.time().toPyTime()
            )
        }

class CreateProjectDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Создание проекта")
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Название проекта
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Название проекта")
        layout.addWidget(self.name_edit)
        
        # Описание проекта
        self.description_edit = QTextEdit()
        self.description_edit.setPlaceholderText("Описание проекта")
        layout.addWidget(self.description_edit)
        
        # Кнопки
        buttons_layout = QHBoxLayout()
        create_btn = QPushButton("Создать")
        cancel_btn = QPushButton("Отмена")
        create_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(create_btn)
        buttons_layout.addWidget(cancel_btn)
        layout.addLayout(buttons_layout)
        
        self.setLayout(layout)

class TeamManagementDialog(QDialog):
    def __init__(self, parent=None, db=None, current_user=None, team_id=None):
        super().__init__(parent)
        self.db = db
        self.current_user = current_user
        self.team_id = team_id
        self.team_info = self.db.get_team_info(team_id)
        self.setWindowTitle(f"Управление командой: {self.team_info[1]}")  # team_info[1] - название команды
        self.resize(800, 600)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Создаем вкладки
        tabs = QTabWidget()
        
        # Вкладка задач
        tasks_tab = QWidget()
        tasks_layout = QVBoxLayout()
        
        # Список задач команды
        tasks_list = QListWidget()
        team_tasks = self.db.get_team_tasks(self.team_id)
        for task in team_tasks:
            item = QListWidgetItem(f"{task.title} (Приоритет: {task.priority})")
            item.setData(Qt.UserRole, task)
            tasks_list.addItem(item)
        
        tasks_layout.addWidget(tasks_list)
        tasks_tab.setLayout(tasks_layout)
        tabs.addTab(tasks_tab, "Задачи")
        
        # Вкладка участников
        members_tab = QWidget()
        members_layout = QVBoxLayout()
        
        # Список участников
        members_list = QListWidget()
        team_members = self.db.get_team_members(self.team_id)
        for member in team_members:
            item = QListWidgetItem(f"{member[1]} ({member[2]})")  # имя и роль
            item.setData(Qt.UserRole, member[0])  # user_id
            members_list.addWidget(item)
        
        members_layout.addWidget(members_list)
        
        # Кнопки управления участниками
        buttons_layout = QHBoxLayout()
        
        invite_btn = QPushButton("Пригласить участника")
        invite_btn.clicked.connect(self.invite_member)
        
        remove_btn = QPushButton("Удалить участника")
        remove_btn.clicked.connect(self.remove_member)
        
        buttons_layout.addWidget(invite_btn)
        buttons_layout.addWidget(remove_btn)
        members_layout.addLayout(buttons_layout)
        
        members_tab.setLayout(members_layout)
        tabs.addTab(members_tab, "Участники")
        
        layout.addWidget(tabs)
        self.setLayout(layout)

    def invite_member(self):
        email, ok = QInputDialog.getText(
            self, 
            "Приглашение участника",
            "Введите email пользователя:"
        )
        if ok and email:
            if self.db.invite_team_member(self.team_id, email):
                QMessageBox.information(self, "Успех", "Приглашение отправлено")
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось отправить приглашение")

    def remove_member(self):
        current_item = self.members_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Ошибка", "Выберите участника для удаления")
            return
            
        user_id = current_item.data(Qt.UserRole)
        if user_id == self.current_user['user_id']:
            QMessageBox.warning(self, "Ошибка", "Вы не можете удалить себя из команды")
            return
            
        reply = QMessageBox.question(
            self,
            "Подтверждение",
            "Вы уверены, что хотите удалить этого участника?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            if self.db.remove_team_member(self.team_id, user_id):
                self.members_list.takeItem(self.members_list.row(current_item))
                QMessageBox.information(self, "Успех", "Участник удален из команды")
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось удалить участника")
