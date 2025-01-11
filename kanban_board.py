from PyQt5.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QLabel, 
                            QScrollArea, QFrame, QPushButton, QSizePolicy, 
                            QMenu, QDialog, QLineEdit, QTextEdit, QDateTimeEdit, 
                            QSpinBox, QMessageBox, QComboBox,QMainWindow)
from PyQt5.QtCore import Qt, QDateTime, QMimeData
from datetime import datetime
from Task import Task
from PyQt5.QtGui import QDrag

class KanbanCard(QFrame):
    def __init__(self, task, parent=None):
        super().__init__(parent)
        self.task = task
        self.init_ui()
        self.setAcceptDrops(True)
        
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
                background-color: #f8f9fa;
                border: 1px solid #ddd;
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
        
        # Добавляем информацию о команде
        if self.task.team_id:
            from database import Database
            db = Database()
            team_name = db.get_team_name(self.task.team_id)
            team_label = QLabel(f"<strong>Команда:</strong> {team_name}")
            team_label.setStyleSheet("color: #555; font-size: 12px; margin: 5px 0;")
            info_layout.addWidget(team_label)
        
        layout.addLayout(info_layout)
    
    def toggle_status(self):
        """Переключение статуса задачи"""
        try:
            current_status = self.task.status
            new_status = None
            
            if current_status == 0:
                new_status = 1  # Новая -> В работе
            elif current_status == 1:
                new_status = 2  # В работе -> Завершено
            elif current_status == 2:
                new_status = 0  # Завершено -> Новая
            else:
                new_status = 0  # Неизвестный статус -> Новая
            
            print(f"[DEBUG] Изменение статуса задачи {self.task.task_id}: {current_status} -> {new_status}")
            
            from database import Database
            db = Database()
            if db.update_task_status(self.task.task_id, new_status):
                self.task.status = new_status  # Обновляем статус в объекте задачи
                
                # Получаем главное окно и обновляем доску
                main_window = None
                current = self
                while current and not isinstance(current, QMainWindow):
                    current = current.parent()
                    if current and hasattr(current, 'func'):
                        main_window = current
                        break
                
                if main_window:
                    print("[DEBUG] Найдено главное окно, обновляем доску")
                    main_window.func.click_input_button()
                else:
                    print("[ERROR] Не удалось найти главное окно")
                    
        except Exception as e:
            print(f"[ERROR] Ошибка при обновлении статуса: {e}")
            import traceback
            traceback.print_exc()
    
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
                from database import Database
                db = Database()
                if db.update_task(self.task):
                    # Обновляем через главное окно
                    from design import Window
                    main_window = self.window()
                    if isinstance(main_window, Window):
                        main_window.click_input_button()
        except Exception as e:
            print(f"Ошибка при редактировании задачи: {e}")
    
    def delete_task(self):
        """Удаление задачи"""
        try:
            reply = QMessageBox.question(
                self, 'Подтверждение',
                'Вы уверены, что хотите удалить эту задачу?',
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                from database import Database
                db = Database()
                if db.delete_task(self.task.task_id):
                    # Обновляем через главное окно
                    from design import Window
                    main_window = self.window()
                    if isinstance(main_window, Window):
                        main_window.click_input_button()
        except Exception as e:
            print(f"Ошибка при удалении задачи: {e}")
    
    def get_priority_color(self):
        colors = {
            1: "#2ecc71",  # Зеленый
            2: "#3498db",  # Синий
            3: "#f1c40f",  # Желтый
            4: "#e67e22",  # Оранжевый
            5: "#e74c3c"   # Красный
        }
        return colors.get(self.task.priority, "#95a5a6")
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            drag = QDrag(self)
            mime = QMimeData()
            mime.setText(str(self.task.task_id))
            drag.setMimeData(mime)
            drag.exec_(Qt.MoveAction)

class KanbanColumn(QWidget):
    def __init__(self, title, status):
        super().__init__()
        self.status = status
        self.color = {
            "new": "light-blue",
            "backlog": "light-yellow",
            "completed": "light-green"
        }.get(status, "white")
        self.init_ui(title)
        
    def init_ui(self, title):
        layout = QVBoxLayout()
        
        # Заголовок колонки
        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet(f"""
            QLabel {{
                background: {self.get_background_color()};
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }}
        """)
        layout.addWidget(title_label)
        
        # Контейнер для карточек
        self.cards_layout = QVBoxLayout()
        self.cards_layout.setAlignment(Qt.AlignTop)
        
        # Создаем виджет для прокрутки
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # Создаем контейнер для карточек
        cards_container = QWidget()
        cards_container.setLayout(self.cards_layout)
        scroll.setWidget(cards_container)
        
        layout.addWidget(scroll)
        self.setLayout(layout)
        
        # Настраиваем прием перетаскивания
        self.setAcceptDrops(True)
        
    def get_background_color(self):
        colors = {
            "light-blue": "#e3f2fd",
            "light-yellow": "#fff3e0",
            "light-green": "#e8f5e9",
            "white": "#ffffff"
        }
        return colors.get(self.color, "#ffffff")
    
    def add_card(self, task):
        """Добавление карточки в колонку"""
        card = KanbanCard(task, self)
        self.cards_layout.addWidget(card)
        print(f"[DEBUG] Добавлена карточка задачи {task.task_id} со статусом {task.status} в колонку {self.status}")
    
    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.accept()
        else:
            event.ignore()
            
    def dropEvent(self, event):
        """Обработка события перетаскивания карточки"""
        try:
            data = event.mimeData().text()
            task_id = int(data)
            
            from database import Database
            db = Database()
            
            # Жестко заданные статусы
            new_status = {
                "new": 0,      # Новые задачи (статус 0)
                "backlog": 1,  # В работе (статус 1)
                "completed": 2 # Завершенные (статус 2)
            }[self.status]
            
            # Обновляем статус задачи в базе данных
            if db.update_task_status(task_id, new_status):
                # Получаем все задачи и обновляем доску
                tasks = db.get_all_tasks()
                self.parent().update_tasks(tasks)
                event.accept()
            else:
                event.ignore()
                
        except Exception as e:
            print(f"[ERROR] Ошибка при перетаскивании: {e}")
            import traceback
            traceback.print_exc()
            event.ignore()

class KanbanBoard(QWidget):
    def __init__(self, project_id=None):
        super().__init__()
        self.project_id = project_id
        self.init_ui()
        
    def init_ui(self):
        layout = QHBoxLayout()
        
        # Создаем колонки
        self.new = KanbanColumn("Новые", "new")
        self.backlog = KanbanColumn("В работе", "backlog")
        self.completed = KanbanColumn("Завершенные", "completed")
        
        layout.addWidget(self.new)
        layout.addWidget(self.backlog)
        layout.addWidget(self.completed)
        
        self.setLayout(layout)
        
    def update_tasks(self, tasks):
        """Обновление задач на доске"""
        print("[DEBUG] Начало обновления задач на доске")
        
        try:
            # Очищаем все колонки
            for column in [self.new, self.backlog, self.completed]:
                while column.cards_layout.count():
                    item = column.cards_layout.takeAt(0)
                    widget = item.widget()
                    if widget:
                        widget.deleteLater()
            
            # Распределяем задачи по колонкам
            for task in tasks:
                status = task.status  # Получаем текущий статус из БД
                print(f"[DEBUG] Распределение задачи {task.task_id}, статус: {status}")
                
                if status == 0:
                    print(f"[DEBUG] Задача {task.task_id} -> Новые")
                    self.new.add_card(task)
                elif status == 1:
                    print(f"[DEBUG] Задача {task.task_id} -> В работе")
                    self.backlog.add_card(task)
                elif status == 2:
                    print(f"[DEBUG] Задача {task.task_id} -> Завершенные")
                    self.completed.add_card(task)
                else:
                    print(f"[WARNING] Неизвестный статус {status}, задача {task.task_id} -> Новые")
                    self.new.add_card(task)
                    
        except Exception as e:
            print(f"[ERROR] Ошибка при обновлении доски: {e}")
            import traceback
            traceback.print_exc()

    def add_task(self, task, status="new"):
        """Добавление задачи в определенную колонку"""
        if status == "backlog":
            task.current_column = 'backlog'
            self.backlog.add_card(task)
        elif status == "completed":
            task.current_column = 'completed'
            self.completed.add_card(task)
        else:
            task.current_column = 'new'
            self.new.add_card(task)

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
                    status=False,  # Новая задача всегда не выполнена
                    notification_time=deadline_edit.dateTime().toPyDateTime(),
                    notified=False,
                    created_at=datetime.now()
                )
                
                if self.parent().func.db.create_task(new_task):
                    self.update_board()  # Обновляем доску сразу после создания
                else:
                    QMessageBox.critical(self, "Ошибка", "Не удалось создать задачу")
                    
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось создать задачу: {str(e)}")
