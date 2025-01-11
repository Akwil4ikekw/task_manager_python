from PyQt5.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QLabel, 
                            QScrollArea, QFrame, QPushButton, QSizePolicy, 
                            QMenu, QDialog, QLineEdit, QTextEdit, QDateTimeEdit, 
                            QSpinBox, QMessageBox, QComboBox)
from PyQt5.QtCore import Qt, QDateTime
from datetime import datetime
from Task import Task

class KanbanCard(QFrame):
    def __init__(self, task, parent=None):
        super().__init__(parent)
        self.task = task
        self.init_ui()
        
    def init_ui(self):
        self.setStyleSheet("""
            QFrame {
                background: #ffffff;
                border: 1px solid #e4e4e4;
                border-radius: 8px;
                margin: 10px 0;
                padding: 15px;
            }
            QFrame:hover {
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.15);
            }
            QPushButton {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 4px;
                padding: 4px 8px;
            }
            QPushButton:hover {
                background-color: #e9ecef;
            }
        """)
        
        layout = QVBoxLayout(self)
        
        # Верхняя часть с заголовком и кнопками
        header_layout = QHBoxLayout()
        
        # Заголовок задачи
        title = QLabel(self.task.title)
        title.setStyleSheet("""
            font-size: 14px;
            font-weight: bold;
            color: #333;
        """)
        header_layout.addWidget(title)
        
        # Кнопки управления
        buttons_layout = QHBoxLayout()
        
        # Кнопка выполнения
        complete_button = QPushButton("✓" if not self.task.status else "↺")
        complete_button.setToolTip("Отметить как выполненное" if not self.task.status else "Отметить как невыполненное")
        complete_button.clicked.connect(self.toggle_status)
        buttons_layout.addWidget(complete_button)
        
        # Кнопка редактирования
        edit_button = QPushButton("✎")
        edit_button.setToolTip("Редактировать")
        edit_button.clicked.connect(self.edit_task)
        buttons_layout.addWidget(edit_button)
        
        # Кнопка удаления
        delete_button = QPushButton("×")
        delete_button.setToolTip("Удалить")
        delete_button.clicked.connect(self.delete_task)
        buttons_layout.addWidget(delete_button)
        
        header_layout.addLayout(buttons_layout)
        layout.addLayout(header_layout)
        
        # Информация о задаче
        info_layout = QVBoxLayout()
        
        # Описание
        if self.task.description:
            desc_label = QLabel(f"<strong>Описание:</strong> {self.task.description}")
            desc_label.setWordWrap(True)
            desc_label.setStyleSheet("color: #555; font-size: 12px; margin: 5px 0;")
            info_layout.addWidget(desc_label)
        
        # Дедлайн
        if self.task.deadline:
            deadline = self.task.deadline.strftime("%d.%m.%Y %H:%M")
            deadline_label = QLabel(f"<strong>Дедлайн:</strong> {deadline}")
            deadline_label.setStyleSheet("color: #555; font-size: 12px; margin: 5px 0;")
            info_layout.addWidget(deadline_label)
        
        # Приоритет
        priority_label = QLabel(f"<strong>Приоритет:</strong> {self.task.priority}")
        priority_label.setStyleSheet(f"""
            color: {self.get_priority_color()};
            font-size: 12px;
            margin: 5px 0;
            font-weight: bold;
        """)
        info_layout.addWidget(priority_label)
        
        layout.addLayout(info_layout)
    
    def toggle_status(self):
        """Переключение статуса задачи"""
        try:
            self.task.status = not self.task.status
            # Обновляем в базе данных
            from database import Database
            db = Database()
            db.update_task_status(self.task.task_id, self.task.status)
            # Обновляем отображение
            self.parent().parent().parent().parent().update_board()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось обновить статус: {str(e)}")
    
    def edit_task(self):
        """Редактирование задачи"""
        try:
            dialog = QDialog(self)
            dialog.setWindowTitle("Редактирование задачи")
            layout = QVBoxLayout(dialog)
            
            # Название
            title_edit = QLineEdit(self.task.title)
            layout.addWidget(QLabel("Название:"))
            layout.addWidget(title_edit)
            
            # Описание
            desc_edit = QTextEdit(self.task.description)
            layout.addWidget(QLabel("Описание:"))
            layout.addWidget(desc_edit)
            
            # Дедлайн
            deadline_edit = QDateTimeEdit(self.task.deadline)
            deadline_edit.setCalendarPopup(True)
            layout.addWidget(QLabel("Дедлайн:"))
            layout.addWidget(deadline_edit)
            
            # Приоритет
            priority_edit = QSpinBox()
            priority_edit.setRange(1, 5)
            priority_edit.setValue(self.task.priority)
            layout.addWidget(QLabel("Приоритет (1-5):"))
            layout.addWidget(priority_edit)
            
            # Кнопки
            buttons = QHBoxLayout()
            save_btn = QPushButton("Сохранить")
            cancel_btn = QPushButton("Отмена")
            
            save_btn.clicked.connect(dialog.accept)
            cancel_btn.clicked.connect(dialog.reject)
            
            buttons.addWidget(save_btn)
            buttons.addWidget(cancel_btn)
            layout.addLayout(buttons)
            
            if dialog.exec_() == QDialog.Accepted:
                # Обновляем данные задачи
                self.task.title = title_edit.text()
                self.task.description = desc_edit.toPlainText()
                self.task.deadline = deadline_edit.dateTime().toPyDateTime()
                self.task.priority = priority_edit.value()
                
                # Сохраняем в базе данных
                from database import Database
                db = Database()
                db.update_task(self.task)
                
                # Обновляем отображение
                self.parent().parent().parent().parent().update_board()
                
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось отредактировать задачу: {str(e)}")
    
    def delete_task(self):
        """Удаление задачи"""
        try:
            reply = QMessageBox.question(self, "Подтверждение", 
                                       "Вы уверены, что хотите удалить эту задачу?",
                                       QMessageBox.Yes | QMessageBox.No)
            
            if reply == QMessageBox.Yes:
                from database import Database
                db = Database()
                db.delete_task(self.task.task_id)
                # Обновляем отображение
                self.parent().parent().parent().parent().update_board()
                
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось удалить задачу: {str(e)}")
    
    def get_priority_color(self):
        colors = {
            1: "#2ecc71",  # Зеленый
            2: "#3498db",  # Синий
            3: "#f1c40f",  # Желтый
            4: "#e67e22",  # Оранжевый
            5: "#e74c3c"   # Красный
        }
        return colors.get(self.task.priority, "#95a5a6")

class KanbanColumn(QWidget):
    def __init__(self, title, color, parent=None):
        super().__init__(parent)
        self.title = title
        self.color = color
        self.init_ui()
        
    def init_ui(self):
        self.setStyleSheet(f"""
            QWidget {{
                background: {self.get_background_color()};
                border-radius: 8px;
                border-top: 5px solid {self.color};
                padding: 15px;
                max-width: 300px;
            }}
        """)
        
        layout = QVBoxLayout(self)
        
        # Заголовок колонки
        title = QLabel(self.title)
        title.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: #333;
            padding-bottom: 5px;
            border-bottom: 2px solid #e9ecef;
            margin-bottom: 15px;
        """)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Контейнер для карточек
        self.cards_widget = QWidget()
        self.cards_layout = QVBoxLayout(self.cards_widget)
        self.cards_layout.setSpacing(10)
        self.cards_layout.setContentsMargins(0, 0, 0, 0)
        
        # Область прокрутки
        scroll = QScrollArea()
        scroll.setWidget(self.cards_widget)
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
        """)
        
        layout.addWidget(scroll)
        layout.addStretch()
        
    def get_background_color(self):
        colors = {
            "#ff6b6b": "#ffecec",  # Для бэклога
            "#ffa500": "#fff3e6",  # Для новых
            "#2ecc71": "#eaffea"   # Для завершенных
        }
        return colors.get(self.color, "#ffffff")
    
    def add_card(self, task):
        card = KanbanCard(task)
        self.cards_layout.insertWidget(0, card)

class KanbanBoard(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.setAcceptDrops(True)
        
    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Создаем колонки в новом порядке
        columns_layout = QHBoxLayout()
        columns_layout.setSpacing(20)
        
        # Новые
        self.new = KanbanColumn("Новые", "#ffa500")
        self.new.setStyleSheet("""
            QWidget {
                background: #fff3e6;
                border-top: 5px solid #ffa500;
                border-radius: 8px;
                padding: 15px;
                max-width: 350px;
            }
        """)
        
        # Беклог
        self.backlog = KanbanColumn("Беклог", "#ff6b6b")
        self.backlog.setStyleSheet("""
            QWidget {
                background: #ffecec;
                border-top: 5px solid #ff6b6b;
                border-radius: 8px;
                padding: 15px;
                max-width: 350px;
            }
        """)
        
        # Завершенные
        self.completed = KanbanColumn("Завершенные", "#2ecc71")
        self.completed.setStyleSheet("""
            QWidget {
                background: #eaffea;
                border-top: 5px solid #2ecc71;
                border-radius: 8px;
                padding: 15px;
                max-width: 350px;
            }
        """)
        
        # Добавляем колонки в новом порядке
        columns_layout.addWidget(self.new)
        columns_layout.addWidget(self.backlog)
        columns_layout.addWidget(self.completed)
        
        main_layout.addLayout(columns_layout)

    def add_task(self, task, status="new"):
        if status == "backlog":
            self.backlog.add_card(task)
        elif status == "new":
            self.new.add_card(task)
        elif status == "completed":
            self.completed.add_card(task)

    def show_create_task_dialog(self):
        """Показать диалог создания задачи"""
        try:
            dialog = QDialog(self)
            dialog.setWindowTitle("Создание новой задачи")
            layout = QVBoxLayout(dialog)
            
            # Название
            title_edit = QLineEdit()
            layout.addWidget(QLabel("Название:"))
            layout.addWidget(title_edit)
            
            # Описание
            desc_edit = QTextEdit()
            layout.addWidget(QLabel("Описание:"))
            layout.addWidget(desc_edit)
            
            # Команда
            team_combo = QComboBox()
            team_combo.addItem("Без команды", None)
            # Получаем список команд пользователя
            from database import Database
            db = Database()
            teams = db.get_user_teams(self.parent().func.current_user['user_id'])
            for team in teams:
                team_combo.addItem(team['name'], team['team_id'])
            layout.addWidget(QLabel("Команда:"))
            layout.addWidget(team_combo)
            
            # Дедлайн
            deadline_edit = QDateTimeEdit(QDateTime.currentDateTime())
            deadline_edit.setCalendarPopup(True)
            layout.addWidget(QLabel("Дедлайн:"))
            layout.addWidget(deadline_edit)
            
            # Приоритет
            priority_edit = QSpinBox()
            priority_edit.setRange(1, 5)
            priority_edit.setValue(3)
            layout.addWidget(QLabel("Приоритет (1-5):"))
            layout.addWidget(priority_edit)
            
            # Кнопки
            buttons = QHBoxLayout()
            save_btn = QPushButton("Создать")
            cancel_btn = QPushButton("Отмена")
            
            save_btn.clicked.connect(dialog.accept)
            cancel_btn.clicked.connect(dialog.reject)
            
            buttons.addWidget(save_btn)
            buttons.addWidget(cancel_btn)
            layout.addLayout(buttons)
            
            if dialog.exec_() == QDialog.Accepted:
                
                new_task = Task(
                    title=title_edit.text(),
                    description=desc_edit.toPlainText(),
                    deadline=deadline_edit.dateTime().toPyDateTime(),
                    priority=priority_edit.value(),
                    user_id=self.parent().func.current_user['user_id'],
                    team_id=team_combo.currentData(),
                    status=False
                )
                
                if self.parent().func.db.create_task(new_task):
                    self.parent().click_input_button()
                else:
                    QMessageBox.critical(self, "Ошибка", "Не удалось создать задачу")
                    
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось создать задачу: {str(e)}")
