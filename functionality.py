from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QInputDialog, QPushButton, QCheckBox, QMessageBox
from database import Database

class Functionality:
    def __init__(self, window):
        self.window = window
        self.db = Database()
        self.current_project_id = None

    def click_input_button(self):
        dlg = QDialog(self.window)
        dlg.setWindowTitle("Сообщение")
        layout = QVBoxLayout()
        label = QLabel("Кнопка Входящие была нажата.")
        layout.addWidget(label)
        dlg.setLayout(layout)
        dlg.exec()

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

    def show_dialog(self):
        # Окно для ввода названия нового проекта
        dlg = QDialog(self.window)
        dlg.setWindowTitle("Добавление проекта")


        input_name, ok = QInputDialog.getText(dlg, "Новый проект", "Название проекта:")
        if ok and input_name:
            self.db.add_project(input_name)
            self.update_projects()



    def show_tasks_window(self, project_id):
        # Окно для отображения задач проекта
        dlg = QDialog(self.window)
        dlg.setWindowTitle("Задачи проекта")
        layout = QVBoxLayout()

        tasks = self.db.get_tasks_by_id(project_id)
        if tasks:
            for task_name, is_completed in tasks:
                checkbox = QCheckBox(task_name, dlg)
                checkbox.setChecked(is_completed)
                layout.addWidget(checkbox)
        else:
            label = QLabel("Нет задач для этого проекта.", dlg)
            layout.addWidget(label)

        # Добавить задачу
        button = QPushButton("Добавить задачу", dlg)
        button.clicked.connect(lambda: self.add_task(project_id))
        layout.addWidget(button)

        dlg.setLayout(layout)
        dlg.exec()

    def update_projects(self):
        try:
            # Очистим текущий список проектов
            for i in reversed(range(self.window.project_list_layout.count())):
                widget = self.window.project_list_layout.itemAt(i).widget()
                if widget:
                    widget.deleteLater()

            # Получение списка проектов из базы данных
            projects = self.db.get_all_projects()

            # Добавляем каждый проект как кнопку
            for project_id, project_name in projects:
                button = QPushButton(project_name)
                button.setStyleSheet(self.window.style_button())
                button.clicked.connect(lambda _, pid=project_id: self.show_tasks_window(pid))
                self.window.project_list_layout.addWidget(button)

        except Exception as e:
            print(f"Ошибка при обновлении проектов: {e}")


    def show_tasks(self, project_id):
        try:
            self.current_project_id = project_id

            # Очистка списка задач
            for i in reversed(range(self.window.task_list_layout.count())):
                widget = self.window.task_list_layout.itemAt(i).widget()
                if widget:
                    widget.deleteLater()

            # Запрос на получение задач для выбранного проекта
            tasks = self.db.get_tasks_by_id(project_id)

            # Добавление задач в виджет
            for name, is_completed in tasks:
                task_label = QLabel(f"Задача: {name}\n Статус: {'Выполнено' if is_completed else 'Не выполнено'}")
                task_label.setStyleSheet("border: 1px solid #ccc; padding: 5px; margin: 5px;")
                self.window.task_list_layout.addWidget(task_label)

        except Exception as e:
            print(f"Ошибка при отображении задач: {e}")

    def add_task(self, project_id):
        try:
            task_name = self.window.new_task_input.text().strip()
            if not task_name:
                return  # Пустое имя задачи

            # Добавление задачи в базу данных
            self.db.add_task_by_id(project_id, task_name)

            # Очистка поля ввода и обновление задач
            self.window.new_task_input.clear()
            self.show_tasks(project_id)

        except Exception as e:
            print(f"Ошибка при добавлении задачи: {e}")

    def handle_project_click(self, project_id, project_name):
        # Сохраняем текущий выбранный проект
        self.current_project_id = project_id
        self.current_project_name = project_name
        
        try:
            # Получаем задачи для выбранного проекта
            tasks = self.get_tasks_for_project(project_id)
            
            # Обновляем интерфейс
            self.window.update_tasks_for_project(project_id, project_name)
            
            # Подсветка выбранного проекта (опционально)
            for button in self.window.findChildren(QPushButton):
                if button.text() == project_name:
                    button.setStyleSheet("""
                        QPushButton {
                            background-color: #4CAF50;
                            color: white;
                            border: none;
                            padding: 8px;
                            border-radius: 4px;
                            text-align: left;
                        }
                    """)
                elif button.parent() == self.window.project_list_widget:  # Проверяем, что это кнопка проекта
                    button.setStyleSheet(self.window.style_button())
                
        except Exception as e:
            QMessageBox.critical(self.window, "Ошибка", f"Не удалось загрузить задачи: {str(e)}")
