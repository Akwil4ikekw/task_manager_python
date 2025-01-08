import psycopg2
from datetime import datetime

class Database:
    def __init__(self):
        # Убедитесь, что в вашем окружении настроены правильные параметры подключения
        self.connection = psycopg2.connect(
            host="localhost",        # Адрес хоста базы данных
            database="Team_task_manager", # Имя вашей базы данных
            user="Aquil",         # Имя пользователя базы данных
            password="123123"  # Пароль пользователя базы данных
        )
        self.connection.autocommit = True  # Включаем автокоммит для запросов (если нужно)

    def register_user(self, username: str, email: str, password: str) -> tuple:
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                """
                INSERT INTO public.personal_user (username, email, password, created_at)
                VALUES (%s, %s, %s, %s)
                RETURNING user_id, username, email, created_at
                """,
                (username, email, password, datetime.now())
            )
            return cursor.fetchone()
        except Exception as e:
            print(f"Ошибка при регистрации пользователя: {e}")
            raise

    def login_user(self, email: str, password: str) -> tuple:
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                """
                SELECT user_id, username, email, created_at
                FROM public.personal_user
                WHERE email = %s AND password = %s
                """,
                (email, password)
            )
            return cursor.fetchone()
        except Exception as e:
            print(f"Ошибка при входе пользователя: {e}")
            raise

    def check_email_exists(self, email: str) -> bool:
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "SELECT user_id FROM public.personal_user WHERE email = %s",
                (email,)
            )
            return cursor.fetchone() is not None
        except Exception as e:
            print(f"Ошибка при проверке email: {e}")
            raise

   