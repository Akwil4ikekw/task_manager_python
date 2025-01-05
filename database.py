import psycopg2

class Database:
    def __init__(self):
        # Убедитесь, что в вашем окружении настроены правильные параметры подключения
        self.connection = psycopg2.connect(
            host="localhost",        # Адрес хоста базы данных
            database="Task_Manager", # Имя вашей базы данных
            user="Aquil",         # Имя пользователя базы данных
            password="123123"  # Пароль пользователя базы данных
        )
        self.connection.autocommit = True  # Включаем автокоммит для запросов (если нужно)

    def close(self):
        """Закрытие соединения с базой данных."""
        if self.connection:
            self.connection.close()

    def add_project(self, project_name):
        cursor = self.connection.cursor()
        cursor.execute("INSERT INTO \"Project\" (name) VALUES (%s)", (project_name,))
        self.connection.commit()

    def add_task(self, project_name, task_name):
        cursor = self.connection.cursor()
        cursor.execute("""
            INSERT INTO "Task" (project_id, name)
            VALUES (
                (SELECT id_project FROM \"Project\" WHERE name = %s),
                %s
            )
        """, (project_name, task_name))
        self.connection.commit()

    def get_tasks(self, project_name):
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT t.name, t.is_completed
            FROM "Task" t
            JOIN "Project" p ON p.id_project = t.project_id
            WHERE p.name = %s
        """, (project_name,))
        return cursor.fetchall()

    def get_all_projects(self):
        cursor = self.connection.cursor()
        cursor.execute("SELECT id_project, name FROM \"Project\" ORDER BY name ASC")
        projects = cursor.fetchall()
        cursor.close()
        return projects

