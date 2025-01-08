from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QInputDialog, QPushButton, QCheckBox,QLineEdit,QHBoxLayout, QMessageBox
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

    def clicked_create_task(self):
        dlg = QDialog(self.window)
        dlg.setWindowTitle("Сообщение")

        dlg.resize(500, 300)
        layout = QVBoxLayout()
    
        task_name = QLineEdit()
        task_name.setPlaceholderText("Введите название задачи")
        
        # Создаем горизонтальный layout для кнопки
        button_layout = QHBoxLayout()
        button_layout.addStretch()  # Добавляем растяжку слева
        
        create_button = QPushButton("Создать задачу")
        create_button.setFixedSize(100, 30)
        button_layout.addWidget(create_button)  # Добавляем кнопку справа
        
        description_task = QLineEdit()
        description_task.setPlaceholderText("Введите описание задачи") 
        description_task.setFixedSize(500,80)


    
        layout.addWidget(task_name)
        layout.addWidget(description_task)
        layout.addStretch()  # Добавляем вертикальную растяжку
        layout.addLayout(button_layout)  # Добавляем горизонтальный layout с кнопкой
        
        def on_create_button_clicked(self):
            pass
        #TODO: Сделать добавление таски в базу данных. Помечая кто и что добавил каким-то хайлайтером
        

        dlg.setLayout(layout)
        dlg.exec()
        
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

            try:
                user_data = self.db.login_user(email.text(), password.text())
                if user_data:
                    self.current_user = {
                        'user_id': user_data[0],
                        'username': user_data[1],
                        'email': user_data[2],
                        'created_at': user_data[3]
                    }
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

            if password.text() != confirm_password.text():
                QMessageBox.warning(dlg, "Ошибка", "Пароли не совпадают")
                return
                
            try:
                # Проверяем, не занят ли email
                if self.db.check_email_exists(email.text()):
                    QMessageBox.warning(dlg, "Ошибка", "�тот email уже зарегистрирован")
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
        