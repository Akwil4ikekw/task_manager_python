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
        """Инициализация интерфейса карточки"""
        layout = QVBoxLayout()
        
        # Верхняя панель с заголовком и кнопками
        top_panel = QHBoxLayout()
        
        # Заголовок
        self.title_label = QLabel(self.task.title)
        self.title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        top_panel.addWidget(self.title_label)
        
        # Растягивающийся элемент
        top_panel.addStretch()
        
        # Кнопка истории
        history_btn = QPushButton("📋")
        history_btn.setFixedSize(24, 24)
        history_btn.setStyleSheet("""
            QPushButton {
                border: none;
                border-radius: 12px;
                background-color: transparent;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
        """)
        history_btn.clicked.connect(self.show_history)
        top_panel.addWidget(history_btn)
        
        # Кнопка комментариев
        comments_btn = QPushButton("💬")
        comments_btn.setFixedSize(24, 24)
        comments_btn.setStyleSheet("""
            QPushButton {
                border: none;
                border-radius: 12px;
                background-color: transparent;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
        """)
        comments_btn.clicked.connect(self.show_comments)
        top_panel.addWidget(comments_btn)
        
        # Кнопка редактирования
        edit_btn = QPushButton("✎")
        edit_btn.setFixedSize(24, 24)
        edit_btn.setStyleSheet("""
            QPushButton {
                border: none;
                border-radius: 12px;
                background-color: transparent;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
        """)
        edit_btn.clicked.connect(self.edit_task)
        top_panel.addWidget(edit_btn)
        
        layout.addLayout(top_panel)
        
        # Описание
        self.description_label = QLabel(self.task.description[:100] + '...' if len(self.task.description) > 100 else self.task.description)
        self.description_label.setWordWrap(True)
        layout.addWidget(self.description_label)
        
        # Дедлайн
        if self.task.deadline:
            self.deadline_label = QLabel(f"Дедлайн: {self.task.deadline.strftime('%d.%m.%Y')}")
            layout.addWidget(self.deadline_label)
        
        # Приоритет
        priority_text = {1: "Низкий", 2: "Средний", 3: "Высокий"}.get(self.task.priority, "Не указан")
        self.priority_label = QLabel(f"Приоритет: {priority_text}")
        layout.addWidget(self.priority_label)
        
        # Добавляем информацию о проекте и команде
        project_name = self.get_project_name()
        team_name = self.get_team_name()
        
        if project_name:
            self.project_label = QLabel(f"Проект: {project_name}")
            layout.addWidget(self.project_label)
        
        if team_name:
            self.team_label = QLabel(f"Команда: {team_name}")
            layout.addWidget(self.team_label)
        
        self.setLayout(layout)
        
        # Устанавливаем цвет фона в зависимости от приоритета
        priority_colors = {
            1: "#E8F5E9",  # светло-зеленый для низкого
            2: "#FFF3E0",  # светло-оранжевый для среднего
            3: "#FFEBEE"   # светло-красный для высокого
        }
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {priority_colors.get(self.task.priority, "#FFFFFF")};
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 8px;
                margin: 4px;
            }}
        """)
        
        # Настраиваем прием перетаскивания
        self.setAcceptDrops(True)
        
    def toggle_status(self):
        """Переключение статуса задачи"""
        try:
            current_status = self.task.status
            new_status = None
            
            if current_status == 0:
                new_status = 2  # Новая -> Выполнено
            elif current_status == 1:
                new_status = 2  # В работе -> Завершено
            elif current_status == 2:
                new_status = 0  # Завершено -> Новая
            
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
            # Получаем главное окно
            main_window = None
            parent = self.parent()
            while parent:
                if isinstance(parent, QMainWindow):
                    main_window = parent
                    break
                parent = parent.parent()
            
            if not main_window or not hasattr(main_window, 'func'):
                QMessageBox.critical(self, "Ошибка", "Не удалось получить доступ к функциям")
                return

            dialog = QDialog(self)
            dialog.setWindowTitle("Редактировать задачу")
            layout = QVBoxLayout()

            # Название
            title_label = QLabel("Название:")
            title_edit = QLineEdit(self.task.title)
            layout.addWidget(title_label)
            layout.addWidget(title_edit)

            # Описание
            description_label = QLabel("Описание:")
            description_edit = QTextEdit()
            description_edit.setText(self.task.description)
            layout.addWidget(description_label)
            layout.addWidget(description_edit)

            # Дедлайн
            deadline_label = QLabel("Дедлайн:")
            deadline_edit = QDateTimeEdit()
            deadline_edit.setDateTime(self.task.deadline if self.task.deadline else QDateTime.currentDateTime())
            deadline_edit.setCalendarPopup(True)
            layout.addWidget(deadline_label)
            layout.addWidget(deadline_edit)

            # Приоритет
            priority_label = QLabel("Приоритет:")
            priority_edit = QSpinBox()
            priority_edit.setMinimum(1)
            priority_edit.setMaximum(3)
            priority_edit.setValue(self.task.priority if self.task.priority else 1)
            layout.addWidget(priority_label)
            layout.addWidget(priority_edit)

            # Кнопки
            buttons = QHBoxLayout()
            save_button = QPushButton("Сохранить")
            cancel_button = QPushButton("Отмена")
            buttons.addWidget(save_button)
            buttons.addWidget(cancel_button)
            layout.addLayout(buttons)

            dialog.setLayout(layout)

            # Подключаем обработчики
            save_button.clicked.connect(dialog.accept)
            cancel_button.clicked.connect(dialog.reject)

            if dialog.exec_() == QDialog.Accepted:
                # Обновляем данные задачи через главное окно
                if main_window.func.db.update_task(
                    task_id=self.task.task_id,
                    title=title_edit.text(),
                    description=description_edit.toPlainText(),
                    deadline=deadline_edit.dateTime().toPyDateTime(),
                    priority=priority_edit.value(),
                    user_id=self.task.user_id,
                    team_id=self.task.team_id
                ):
                    # Обновляем локальный объект задачи
                    self.task.title = title_edit.text()
                    self.task.description = description_edit.toPlainText()
                    self.task.deadline = deadline_edit.dateTime().toPyDateTime()
                    self.task.priority = priority_edit.value()
                    
                    # Обновляем отображение
                    self.update_display()
                    QMessageBox.information(self, "Успех", "Задача обновлена")
                else:
                    QMessageBox.critical(self, "Ошибка", "Не удалось обновить задачу")

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при редактировании задачи: {str(e)}")
    
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
    
    def show_history(self):
        """Показать историю изменений задачи"""
        try:
            main_window = self.get_main_window()
            if not main_window or not hasattr(main_window, 'func'):
                QMessageBox.warning(self, "Ошибка", "Не удалось получить доступ к функциям")
                return
            
            dialog = QDialog(self)
            dialog.setWindowTitle(f"История изменений задачи: {self.task.title}")
            dialog.resize(600, 400)
            layout = QVBoxLayout()

            # Область для истории
            history_area = QTextEdit()
            history_area.setReadOnly(True)
            layout.addWidget(history_area)

            # Получаем историю
            history = main_window.func.db.get_task_history(self.task.task_id)
            
            # Форматируем историю
            html_content = "<style>"
            html_content += "p { margin: 5px 0; }"
            html_content += ".username { color: #4CAF50; font-weight: bold; }"
            html_content += ".timestamp { color: #666; font-size: 0.9em; }"
            html_content += ".change { margin: 10px 0; padding: 10px; background-color: #f8f9fa; }"
            html_content += "</style>"
            
            for record in history:
                history_id, timestamp, username, old_status, new_status, old_priority, new_priority, \
                old_deadline, new_deadline, old_description, new_description, change_type = record
                
                html_content += f'<div class="change">'
                html_content += f'<span class="username">{username}</span> '
                html_content += f'<span class="timestamp">{timestamp.strftime("%d.%m.%Y %H:%M")}</span>'
                
                # Подробное описание изменений
                if change_type == 'update_title':
                    html_content += f'<p>Изменено название задачи:<br>'
                    html_content += f'Было: {old_description}<br>'
                    html_content += f'Стало: {new_description}</p>'
                elif change_type == 'update_description':
                    html_content += f'<p>Изменено описание задачи:<br>'
                    html_content += f'Было: {old_description}<br>'
                    html_content += f'Стало: {new_description}</p>'
                elif change_type == 'update_status':
                    status_text = {True: "Завершена", False: "В работе"}
                    html_content += f'<p>Изменен статус задачи:<br>'
                    html_content += f'Было: {status_text.get(old_status, "Не указан")}<br>'
                    html_content += f'Стало: {status_text.get(new_status, "Не указан")}</p>'
                elif change_type == 'update_priority':
                    priority_text = {1: "Низкий", 2: "Средний", 3: "Высокий"}
                    html_content += f'<p>Изменен приоритет задачи:<br>'
                    html_content += f'Было: {priority_text.get(old_priority, "Не указан")}<br>'
                    html_content += f'Стало: {priority_text.get(new_priority, "Не указан")}</p>'
                elif change_type == 'update_deadline':
                    old_date = old_deadline.strftime("%d.%m.%Y") if old_deadline else "Не указан"
                    new_date = new_deadline.strftime("%d.%m.%Y") if new_deadline else "Не указан"
                    html_content += f'<p>Изменен дедлайн задачи:<br>'
                    html_content += f'Было: {old_date}<br>'
                    html_content += f'Стало: {new_date}</p>'
                elif change_type == 'add_comment':
                    html_content += f'<p>Добавлен комментарий:<br>{new_description}</p>'
                elif change_type == 'create_task':
                    html_content += f'<p>Создана новая задача</p>'
                elif change_type == 'delete_task':
                    html_content += f'<p>Задача удалена</p>'
                
                html_content += '</div>'
                
            history_area.setHtml(html_content)

            # Кнопка закрытия
            close_btn = QPushButton("Закрыть")
            close_btn.clicked.connect(dialog.accept)
            layout.addWidget(close_btn)

            dialog.setLayout(layout)
            dialog.exec_()
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при отображении истории: {str(e)}")

    def show_comments(self):
        """Показать комментарии к задаче"""
        try:
            main_window = self.get_main_window()
            if not main_window or not hasattr(main_window, 'func'):
                QMessageBox.warning(self, "Ошибка", "Не удалось получить доступ к функциям")
                return

            dialog = QDialog(self)
            dialog.setWindowTitle(f"Комментарии к задаче: {self.task.title}")
            dialog.resize(400, 500)
            layout = QVBoxLayout()

            # Область для существующих комментариев
            comments_area = QTextEdit()
            comments_area.setReadOnly(True)
            layout.addWidget(comments_area)

            # Получаем комментарии через главное окно
            comments = main_window.func.db.get_task_comments(self.task.task_id)
            
            # Форматируем и отображаем комментарии
            html_content = "<style>"
            html_content += "p { margin: 5px 0; }"
            html_content += ".username { color: #4CAF50; font-weight: bold; }"
            html_content += ".timestamp { color: #666; font-size: 0.9em; }"
            html_content += ".comment { margin: 10px 0; padding: 5px; background-color: #f8f9fa; }"
            html_content += "</style>"
            
            for comment in comments:
                comment_id, text, created_at, username, user_id = comment
                html_content += f'<div class="comment">'
                html_content += f'<span class="username">{username}</span> '
                html_content += f'<span class="timestamp">{created_at.strftime("%d.%m.%Y %H:%M")}</span>'
                html_content += f'<p>{text}</p>'
                html_content += '</div>'
                
            comments_area.setHtml(html_content)

            # Поле для нового комментария
            new_comment = QTextEdit()
            new_comment.setPlaceholderText("Введите комментарий...")
            new_comment.setMaximumHeight(100)
            layout.addWidget(new_comment)

            # Кнопки
            buttons = QHBoxLayout()
            add_btn = QPushButton("Добавить комментарий")
            close_btn = QPushButton("Закрыть")
            
            # Используем main_window.func при добавлении комментария
            add_btn.clicked.connect(lambda: self.add_comment(new_comment.toPlainText(), dialog, main_window.func))
            close_btn.clicked.connect(dialog.accept)
            
            buttons.addWidget(add_btn)
            buttons.addWidget(close_btn)
            layout.addLayout(buttons)

            dialog.setLayout(layout)
            dialog.exec_()
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при отображении комментариев: {str(e)}")

    def add_comment(self, comment_text: str, dialog: QDialog, func):
        """Добавление нового комментария"""
        if not comment_text.strip():
            QMessageBox.warning(self, "Ошибка", "Комментарий не может быть пустым")
            return
        
        try:
            if func.db.add_comment_to_task(
                self.task.task_id,
                func.current_user['user_id'],
                comment_text
            ):
                QMessageBox.information(self, "Успех", "Комментарий добавлен")
                dialog.accept()
            else:
                QMessageBox.critical(self, "Ошибка", "Не удалось добавить комментарий")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при добавлении комментария: {str(e)}")

    def update_display(self):
        """Обновление отображения карточки"""
        try:
            # Обновляем заголовок
            self.title_label.setText(self.task.title)
            
            # Обновляем описание
            if hasattr(self, 'description_label'):
                self.description_label.setText(self.task.description[:100] + '...' if len(self.task.description) > 100 else self.task.description)
            
            # Обновляем дедлайн
            if hasattr(self, 'deadline_label') and self.task.deadline:
                self.deadline_label.setText(f"Дедлайн: {self.task.deadline.strftime('%d.%m.%Y')}")
            
            # Обновляем приоритет
            if hasattr(self, 'priority_label'):
                priority_text = {1: "Низкий", 2: "Средний", 3: "Высокий"}.get(self.task.priority, "Не указан")
                self.priority_label.setText(f"Приоритет: {priority_text}")
            
            # Обновляем стиль в зависимости от приоритета
            priority_colors = {
                1: "#E8F5E9",  # светло-зеленый для низкого
                2: "#FFF3E0",  # светло-оранжевый для среднего
                3: "#FFEBEE"   # светло-красный для высокого
            }
            self.setStyleSheet(f"""
                QFrame {{
                    background-color: {priority_colors.get(self.task.priority, "#FFFFFF")};
                    border: 1px solid #ddd;
                    border-radius: 4px;
                    padding: 8px;
                    margin: 4px;
                }}
            """)
            
            # Перерисовываем виджет
            self.update()
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при обновлении отображения: {str(e)}")

    def get_project_name(self):
        """Получение названия проекта"""
        try:
            main_window = self.get_main_window()
            if main_window and hasattr(main_window, 'func'):
                cursor = main_window.func.db.connection.cursor()
                cursor.execute("""
                    SELECT p.name 
                    FROM project p
                    JOIN tasks t ON t.project_id = p.project_id
                    WHERE t.task_id = %s
                """, (self.task.task_id,))
                result = cursor.fetchone()
                return result[0] if result else "Не указан"
        except Exception as e:
            print(f"Ошибка при получении проекта: {e}")
        return "Не указан"

    def get_team_name(self):
        """Получение названия команды"""
        try:
            main_window = self.get_main_window()
            if main_window and hasattr(main_window, 'func'):
                cursor = main_window.func.db.connection.cursor()
                cursor.execute("""
                    SELECT name FROM team WHERE team_id = %s
                """, (self.task.team_id,))
                result = cursor.fetchone()
                return result[0] if result else "Не указана"
        except Exception as e:
            print(f"Ошибка при получении команды: {e}")
        return "Не указана"

    def get_main_window(self):
        """Получение главного окна"""
        parent = self.parent()
        while parent:
            if isinstance(parent, QMainWindow):
                return parent
            parent = parent.parent()
        return None

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
