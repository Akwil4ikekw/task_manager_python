import psycopg2
from datetime import datetime
from Task import Task
from Team import Team
import hashlib

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
            self.connection.autocommit = True
            
            # Создаем/обновляем таблицы
            self.create_tables()
            self.update_tasks_table()  # Добавляем вызов метода обновления
            
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
        try:
            cursor = self.connection.cursor()
            query = """
                INSERT INTO tasks (
                    title, description, user_id, status, deadline, 
                    project_id, team_id, priority, notification_time, 
                    notified, created_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING task_id
            """
            values = (
                task.title,
                task.description,
                task.user_id,
                task.status,
                task.deadline,
                task.project_id,
                task.team_id,
                task.priority,
                task.notification_time,
                task.notified,
                task.created_at
            )
            print("SQL Query:", query)
            print("Values:", values)
            cursor.execute(query, values)
            self.connection.commit()  # Добавляем явный commit
            task_id = cursor.fetchone()[0]
            return task_id
        except Exception as e:
            print(f"Ошибка при добавлении задачи:")
            print(f"Тип ошибки: {type(e).__name__}")
            print(f"Текст ошибки: {str(e)}")
            import traceback
            traceback.print_exc()
            return None

    def get_user_teams(self, user_id: int) -> list:
        """Получение списка команд пользователя"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT t.team_id, t.name, t.description
                FROM team t
                JOIN team_member tm ON t.team_id = tm.team_id
                WHERE tm.user_id = %s
            """, (user_id,))
            
            teams = []
            for row in cursor.fetchall():
                teams.append({
                    'team_id': row[0],
                    'name': row[1],
                    'description': row[2]
                })
            return teams
        except Exception as e:
            print(f"Ошибка при получении списка команд: {e}")
            return []

    def create_team(self, name: str, description: str, creator_id: int, icon_path: str = None) -> int:
        """Создание команды"""
        try:
            cursor = self.connection.cursor()
            
            # Создаем команду
            cursor.execute("""
                INSERT INTO team (name, description, creator_id, created_at, icon_path)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING team_id
            """, (name, description, creator_id, datetime.now(), icon_path))
            
            team_id = cursor.fetchone()[0]
            
            # Добавляем создателя как администратора команды
            cursor.execute("""
                INSERT INTO team_member (team_id, user_id, role)
                VALUES (%s, %s, %s)
            """, (team_id, creator_id, 'admin'))
            
            self.connection.commit()
            return team_id
            
        except Exception as e:
            print(f"Ошибка при создании команды: {e}")
            import traceback
            traceback.print_exc()
            self.connection.rollback()
            return None

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

    def get_project_tasks(self, project_id: int) -> list:
        """Получение всех задач проекта"""
        try:
            print(f"\n=== Получение задач для проекта {project_id} ===")
            cursor = self.connection.cursor()
            query = """
                SELECT task_id, title, description, user_id, status, deadline, 
                       priority, project_id, team_id, notification_time, 
                       notified, created_at
                FROM tasks 
                WHERE project_id = %s
                ORDER BY deadline ASC
            """
            print(f"SQL Query: {query}")
            print(f"Project ID: {project_id}")
            
            cursor.execute(query, (project_id,))
            rows = cursor.fetchall()
            print(f"Получено строк из БД: {len(rows)}")
            
            tasks = []
            for row in rows:
                print(f"\nОбработка строки: {row}")
                task = Task(
                    title=row[1],
                    description=row[2],
                    user_id=row[3],
                    status=row[4],
                    deadline=row[5],
                    priority=row[6],
                    project_id=row[7],
                    team_id=row[8],
                    notification_time=row[9],
                    notified=row[10],
                    created_at=row[11]
                )
                task.task_id = row[0]
                tasks.append(task)
                print(f"Создан объект Task: {task.__dict__}")
            
            print(f"\nВсего создано объектов Task: {len(tasks)}")
            return tasks
        except Exception as e:
            print(f"\n=== Ошибка при получении задач проекта ===")
            print(f"Тип ошибки: {type(e).__name__}")
            print(f"Текст ошибки: {str(e)}")
            import traceback
            traceback.print_exc()
            return []

    def get_project_info(self, project_id: int) -> dict:
        """Получение информации о проекте"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT project_id, name, description, team_id, created_at
                FROM project 
                WHERE project_id = %s
            """, (project_id,))
            
            project = cursor.fetchone()
            if project:
                return {
                    'project_id': project[0],
                    'name': project[1],
                    'description': project[2],
                    'team_id': project[3],
                    'created_at': project[4]
                }
            return None
        except Exception as e:
            print(f"Ошибка при получении информации о проекте: {e}")
            return None

    def create_tables(self):
        """Создание необходимых таблиц"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    task_id SERIAL PRIMARY KEY,
                    title VARCHAR(255) NOT NULL,
                    description TEXT,
                    user_id INTEGER REFERENCES personal_user(user_id),
                    status BOOLEAN DEFAULT FALSE,
                    deadline TIMESTAMP,
                    priority INTEGER DEFAULT 1,
                    project_id INTEGER REFERENCES project(project_id),
                    team_id INTEGER REFERENCES team(team_id),
                    notification_time TIMESTAMP,
                    notified BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            self.connection.commit()
            print("Таблица tasks успешно создана")
        except Exception as e:
            print(f"Ошибка при создании таблиц: {e}")

    def update_tasks_table(self):
        """Обновление структуры таблицы tasks"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                DO $$ 
                BEGIN 
                    BEGIN
                        ALTER TABLE tasks DROP COLUMN IF EXISTS start;
                    EXCEPTION
                        WHEN undefined_column THEN NULL;
                    END;
                END $$;
            """)
            self.connection.commit()
            print("Структура таблицы tasks успешно обновлена")
        except Exception as e:
            print(f"Ошибка при обновлении таблицы tasks: {e}")

    def get_team_name(self, team_id: int) -> str:
        """Получение названия команды по ID"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT name 
                FROM team 
                WHERE team_id = %s
            """, (team_id,))
            result = cursor.fetchone()
            return result[0] if result else "Без команды"
        except Exception as e:
            print(f"Ошибка при получении названия команды: {e}")
            return "Без команды"

    def get_user_tasks(self, user_id: int) -> list:
        """Получение всех задач пользователя"""
        try:
            print(f"\n=== Получение задач для пользователя {user_id} ===")
            cursor = self.connection.cursor()
            query = """
                SELECT task_id, title, description, user_id, status, deadline, 
                       priority, project_id, team_id, notification_time, 
                       notified, created_at
                FROM tasks 
                WHERE user_id = %s
                ORDER BY created_at DESC
            """
            print(f"SQL Query: {query}")
            cursor.execute(query, (user_id,))
            
            rows = cursor.fetchall()
            print(f"Получено строк из БД: {len(rows)}")
            
            tasks = []
            for row in rows:
                print(f"\nОбработка строки: {row}")
                task = Task(
                    title=row[1],
                    description=row[2],
                    user_id=row[3],
                    status=row[4],
                    deadline=row[5],
                    priority=row[6],
                    project_id=row[7],
                    team_id=row[8],
                    notification_time=row[9],
                    notified=row[10],
                    created_at=row[11]
                )
                task.task_id = row[0]
                tasks.append(task)
                print(f"Создан объект Task: {task.__dict__}")
            
            print(f"\nВсего создано объектов Task: {len(tasks)}")
            return tasks
        except Exception as e:
            print(f"\n=== Ошибка при получении задач пользователя ===")
            print(f"Тип ошибки: {type(e).__name__}")
            print(f"Текст ошибки: {str(e)}")
            import traceback
            traceback.print_exc()
            return []

    def update_task_status(self, task_id: int, status: bool) -> bool:
        """Обновление статуса задачи"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                UPDATE tasks 
                SET status = %s 
                WHERE task_id = %s
            """, (status, task_id))
            self.connection.commit()
            return True
        except Exception as e:
            print(f"Ошибка при обновлении статуса задачи: {e}")
            self.connection.rollback()
            return False

    def update_task(self, task) -> bool:
        """Обновление задачи"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                UPDATE tasks 
                SET title = %s, description = %s, deadline = %s, 
                    priority = %s, notification_time = %s
                WHERE task_id = %s
            """, (task.title, task.description, task.deadline, 
                  task.priority, task.notification_time, task.task_id))
            self.connection.commit()
            return True
        except Exception as e:
            print(f"Ошибка при обновлении задачи: {e}")
            self.connection.rollback()
            return False

    def delete_task(self, task_id: int) -> bool:
        """Удаление задачи"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                DELETE FROM tasks 
                WHERE task_id = %s
            """, (task_id,))
            self.connection.commit()
            return True
        except Exception as e:
            print(f"Ошибка при удалении задачи: {e}")
            self.connection.rollback()
            return False

    def get_project_name(self, project_id: int) -> str:
        """Получение названия проекта по ID"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT name 
                FROM project 
                WHERE project_id = %s
            """, (project_id,))
            result = cursor.fetchone()
            return result[0] if result else "Без проекта"
        except Exception as e:
            print(f"Ошибка при получении названия проекта: {e}")
            return "Без проекта"

   