import sys
from PyQt5.QtWidgets import QApplication
from design import Window
import psycopg2
from psycopg2 import Error
import os
import subprocess

# def init_database():
#     try:
#         # Подключаемся к postgres
#         connection = psycopg2.connect(
#             user="postgres",
#             password="postgres",
#             host="localhost",
#             port="5432",
#             database="Task_manager"
#         )
#         connection.autocommit = True
#         cursor = connection.cursor()
        
#         # Получаем абсолютный путь к bd.sql
#         current_dir = os.path.dirname(os.path.abspath(__file__))
#         dump_file = os.path.join(current_dir, 'bd.sql')
        
#         print(f"Путь к файлу дампа: {dump_file}")  # Для отладки
#         print(f"Файл существует: {os.path.exists(dump_file)}")  # Проверка существования файла
        
#         # Используем полный путь к pg_restore
#         restore_command = [
#             r'C:\Program Files\PostgreSQL\15\bin\pg_restore',  # Обновленный путь для версии 15
#             '-h', 'localhost',
#             '-p', '5432',
#             '-U', 'postgres',
#             '-d', 'postgres',
#             '-c',
#             dump_file
#         ]
        
#         # Выполняем восстановление
#         process = subprocess.Popen(
#             restore_command,
#             env={'PGPASSWORD': 'postgres'},
#             stdout=subprocess.PIPE,
#             stderr=subprocess.PIPE
#         )
        
#         output, error = process.communicate()
        
#         if process.returncode != 0:
#             print("Вывод pg_restore:", output.decode() if output else "Нет вывода")
#             print("Ошибка pg_restore:", error.decode() if error else "Нет ошибок")
#             return None
            
#         print("База данных успешно восстановлена!")
#         return connection
        
#     except (Exception, Error) as error:
#         print(f"Ошибка при инициализации базы данных: {str(error)}")
#         return None

def main():
    app = QApplication(sys.argv)
    
    # Инициализируем БД и получаем подключение
    #db_connection = init_database()
    
    window = Window()
    # if db_connection:
    #     window.db_connection = db_connection
    window.show()
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()

