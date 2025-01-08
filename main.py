from PyQt5.QtWidgets import QApplication
import sys
from design import Window

app = QApplication(sys.argv)
window = Window()

# Показываем окно входа
# if  window.func.show_login_window():
#     # Если вход успешный, показываем главное окно
#     window.showMaximized()
# else:
#     # Если пользователь отменил вход, закрываем приложение
#     sys.exit()

sys.exit(app.exec())

