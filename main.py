from PyQt5.QtWidgets import QApplication
import sys
from design import Window



app = QApplication(sys.argv)

# Создаем окно приложения
window = Window()

# Запуск приложения
sys.exit(app.exec())

