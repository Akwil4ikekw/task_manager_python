import sys
from PyQt5.QtWidgets import QApplication
from design import Window

def main():
    app = QApplication(sys.argv)
    window = Window()
    window.show()  # Показываем основное окно
    
    # Показываем окно входа
    if not window.func.is_authenticated():
        window.func.show_login_window()
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()

