import psycopg2
from datetime import datetime
from Task import Task
from Team import Team

class Database:
    def __init__(self):
        try:
            self.connection = psycopg2.connect(
                database='Team_task_manager',
                user='Aquil',
                password='123123',
                host='localhost',
                port='5432'
            )
            self.connection.autocommit = True  # Включаем автокоммит для запросов (если нужно)
        except Exception as e:
            print(f"Ошибка при подключении к базе данных: {e}")

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

    def create_task(self, task: Task) -> int:
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                """
                INSERT INTO public.task (
                    title, description, user_id, status, 
                    deadline, priority, project_id, team_id
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING task_id
                """,
                (
                    task.name, task.description, task.user_id,
                    task.status, task.deadline, task.priority,
                    task.project_id, task.team_id
                )
            )
            return cursor.fetchone()[0]
        except Exception as e:
            print(f"Ошибка при создании задачи: {e}")
            raise

    def add_task(self, task):
        """Добавляет новую задачу в базу данных"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                INSERT INTO task (
                    title, 
                    description, 
                    user_id, 
                    status, 
                    deadline, 
                    project_id,
                    team_id,
                    priority,
                    notification_time,
                    notified,
                    created_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING task_id
            """, (
                task.title,
                task.description,
                task.user_id,
                task.status,
                datetime.fromtimestamp(task.deadline),
                task.project_id,
                task.team_id,
                task.priority,
                datetime.fromtimestamp(task.notification_time),
                task.notified,
                datetime.fromtimestamp(task.created_at)
            ))
            task_id = cursor.fetchone()[0]
            return task_id
        except Exception as e:
            print(f"Ошибка при добавлении задачи: {e}")
            return None

    def get_user_teams(self, user_id: int) -> list:
        """Получает список команд, в которых состоит пользователь"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT t.team_id, t.name, t.description, tm.role
                FROM team t
                JOIN team_member tm ON t.team_id = tm.team_id
                WHERE tm.user_id = %s
                ORDER BY t.created_at DESC
            """, (user_id,))
            return cursor.fetchall()
        except Exception as e:
            print(f"Ошибка при получении списка команд: {e}")
            return []

    def create_team(self, name: str, description: str, icon_path: str) -> int:
        """Создает новую команду"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                INSERT INTO team (name, description, icon_path, created_at)
                VALUES (%s, %s, %s, %s)
                RETURNING team_id
            """, (name, description, icon_path, datetime.now()))
            return cursor.fetchone()[0]
        except Exception as e:
            print(f"Ошибка при создании команды: {e}")
            raise

    def add_team_member(self, team_id: int, user_id: int, role: str = 'member') -> None:
        """Добавляет пользователя в команду"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                INSERT INTO team_member (team_id, user_id, role)
                VALUES (%s, %s, %s)
            """, (team_id, user_id, role))
        except Exception as e:
            print(f"Ошибка при добавлении участника команды: {e}")
            raise
        

    def get_team_projects(self, team_id: int) -> list:
        """Получает список проектов команды"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT project_id, name, description, created_at
                FROM project
                WHERE team_id = %s
                ORDER BY created_at DESC
            """, (team_id,))
            return cursor.fetchall()
        except Exception as e:
            print(f"Ошибка при получении проектов команды: {e}")
            return []

    def create_project(self, name: str, description: str, team_id: int) -> int:
        """Создает новый проект"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                INSERT INTO project (name, description, team_id, created_at)
                VALUES (%s, %s, %s, %s)
                RETURNING project_id
            """, (name, description, team_id, datetime.now()))
            return cursor.fetchone()[0]
        except Exception as e:
            print(f"Ошибка при создании проекта: {e}")
            raise

    def get_team_members(self, team_id: int) -> list:
        """Получает список участников команды"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT u.user_id, u.username, tm.role
                FROM personal_user u
                JOIN team_member tm ON u.user_id = tm.user_id
                WHERE tm.team_id = %s
            """, (team_id,))
            return cursor.fetchall()
        except Exception as e:
            print(f"Ошибка при получении участников команды: {e}")
            return []

    def invite_user_to_team(self, user_id, team_id):
        try:
            self.cursor.execute("""
                INSERT INTO user_team (user_id, team_id, role)
                VALUES (%s, %s, 'member')
            """, (user_id, team_id))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Ошибка при добавлении пользователя в команду: {e}")
            return False

    def get_users_not_in_team(self, team_id):
        try:
            self.cursor.execute("""
                SELECT user_id, username, email 
                FROM personal_user 
                WHERE user_id NOT IN (
                    SELECT user_id FROM user_team 
                    WHERE team_id = %s
                )
            """, (team_id,))
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Ошибка при получении списка пользователей вне команды: {e}")
            return []

    def get_user_by_email(self, email, team_id):
        try:
            cursor = self.connection.cursor()
            # Сначала получаем данные пользователя
            cursor.execute("""
                SELECT user_id, username, email 
                FROM personal_user 
                WHERE email = %s
            """, (email,))
            user = cursor.fetchone()
            
            if not user:
                return None  # Пользователь не найден
            
            # Проверяем, не состоит ли он уже в команде
            cursor.execute("""
                SELECT user_id FROM user_team 
                WHERE user_id = %s AND team_id = %s
            """, (user[0], team_id))
            
            if cursor.fetchone():
                return None  # Пользователь уже в команде
            
            return user
        except Exception as e:
            print(f"Ошибка при получении пользователя по email: {e}")
            return None

    def search_users(self, search_text, team_id):
        try:
            self.cursor.execute("""
                SELECT user_id, username, email 
                FROM personal_user 
                WHERE (email ILIKE %s OR username ILIKE %s)
                AND user_id NOT IN (
                    SELECT user_id FROM user_team 
                    WHERE team_id = %s
                )
            """, (f'%{search_text}%', f'%{search_text}%', team_id))
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Ошибка при поиске пользователей: {e}")
            return []

   