from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                            QLineEdit, QTextEdit, QPushButton, QComboBox, 
                            QCalendarWidget, QTimeEdit)
from PyQt5.QtCore import Qt, QTime
from datetime import datetime

class CreateTaskDialog(QDialog):
    def __init__(self, parent=None, status=None):
        super().__init__(parent)
        self.setWindowTitle("Создание задачи")
        self.setup_ui()
        self.status = status

    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Название задачи
        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("Название задачи")
        layout.addWidget(self.title_edit)
        
        # Описание
        self.description_edit = QTextEdit()
        self.description_edit.setPlaceholderText("Описание задачи")
        layout.addWidget(self.description_edit)
        
        # Приоритет
        priority_layout = QHBoxLayout()
        priority_label = QLabel("Приоритет:")
        self.priority_combo = QComboBox()
        self.priority_combo.addItems(['1', '2', '3', '4', '5'])
        priority_layout.addWidget(priority_label)
        priority_layout.addWidget(self.priority_combo)
        layout.addLayout(priority_layout)
        
        # Дедлайн
        deadline_layout = QHBoxLayout()
        deadline_label = QLabel("Дедлайн:")
        self.deadline_edit = QCalendarWidget()
        deadline_layout.addWidget(deadline_label)
        deadline_layout.addWidget(self.deadline_edit)
        layout.addLayout(deadline_layout)
        
        # Время дедлайна
        self.time_edit = QTimeEdit()
        self.time_edit.setTime(QTime.currentTime())
        layout.addWidget(self.time_edit)
        
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
