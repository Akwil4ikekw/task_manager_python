import sys
from PyQt5.QtWidgets import QApplication
from design import Window
import psycopg2
from psycopg2 import Error
import os
import subprocess 


def init_database():
    try:
        # Подключаемся к postgres
        connection = psycopg2.connect(
            user='postgres',
            password='123123',           # Используем пароль 123123
            host='localhost',
            port='5432',
            database='postgres'          # Сначала подключаемся к postgres
        )
        connection.autocommit = True
        cursor = connection.cursor()
        
        # Получаем путь к файлу дампа
        current_dir = os.path.dirname(os.path.abspath(__file__))
        dump_file = os.path.join(current_dir, 'bd.sql')
        
        print(f"Путь к файлу дампа: {dump_file}")
        print(f"Файл существует: {os.path.exists(dump_file)}")
        
        # Используем pg_restore с правильными учетными данными
        restore_command = [
            r'C:\Program Files\PostgreSQL\15\bin\pg_restore',
            '-h', 'localhost',
            '-p', '5432',
            '-U', 'postgres',
            '-d', 'Team_task_manager',    # Имя вашей БД
            '-c',                         # Очищаем существующие данные
            dump_file
        ]
        
        # Выполняем восстановление с правильным паролем
        process = subprocess.Popen(
            restore_command,
            env={'PGPASSWORD': '123123'},  # Устанавливаем пароль через переменную окружения
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        output, error = process.communicate()
        
        if process.returncode != 0:
            print("Вывод pg_restore:", output.decode() if output else "Нет вывода")
            print("Ошибка pg_restore:", error.decode() if error else "Нет ошибок")
            return None
            
        print("База данных успешно восстановлена!")
        
        # Возвращаем подключение к восстановленной БД
        return psycopg2.connect(
            database='Team_task_manager',
            user='postgres',
            password='123123',
            host='localhost',
            port='5432'
        )
        
    except Exception as e:
        print(f"Ошибка при инициализации базы данных: {str(e)}")
        return None

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

