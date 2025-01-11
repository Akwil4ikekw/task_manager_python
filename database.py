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

    def create_task(self, task: Task) -> bool:
        """Создание новой задачи"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                INSERT INTO tasks (
                    title, description, deadline, priority,
                    project_id, team_id, user_id, created_at,
                    notification_time, notified, status
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                ) RETURNING task_id
            """, (
                task.title,  # Используем title вместо name
                task.description,
                task.deadline,
                task.priority,
                task.project_id,
                task.team_id,
                task.user_id,
                task.created_at,
                task.notification_time,
                task.notified,
                task.status
            ))
            
            task_id = cursor.fetchone()[0]
            self.connection.commit()
            print(f"Создана задача с ID: {task_id}")
            return True
            
        except Exception as e:
            print(f"Ошибка при создании задачи: {e}")
            self.connection.rollback()
            return False

    def add_task(self, task: Task) -> int:
        """Добавление новой задачи"""
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
            cursor.execute(query, values)
            task_id = cursor.fetchone()[0]
            self.connection.commit()
            return task_id
        except Exception as e:
            print(f"Ошибка при добавлении задачи: {e}")
            self.connection.rollback()
            return None

    def get_user_teams(self, user_id: int) -> list:
        """Получение списка команд пользователя"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT t.team_id, t.name, t.description, 
                       tm.role, 
                       COALESCE(t.icon_path, 'default_icon.png') as icon_path,
                       (SELECT COUNT(*) FROM team_member WHERE team_id = t.team_id) as member_count
                FROM team t
                JOIN team_member tm ON t.team_id = tm.team_id
                WHERE tm.user_id = %s
                ORDER BY t.name
            """, (user_id,))
            return cursor.fetchall()
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

    def add_team_member(self, team_id: int, user_id: int, added_by_id: int) -> bool:
        """Добавление участника в команду"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT username FROM personal_user WHERE user_id = %s
            """, (user_id,))
            user_info = cursor.fetchone()
            
            if user_info:
                # Логируем добавление участника
                self.add_task_history(
                    task_id=0,
                    user_id=added_by_id,
                    team_id=team_id,
                    new_description=f"Добавлен участник: {user_info[0]}",
                    change_type='add_team_member'
                )
            
            cursor.execute("""
                INSERT INTO team_member (team_id, user_id, role)
                VALUES (%s, %s, 'member')
            """, (team_id, user_id))
            
            self.connection.commit()
            return True
        except Exception as e:
            print(f"Ошибка при добавлении участника: {e}")
            self.connection.rollback()
            return False

    def get_team_projects(self, team_id: int) -> list:
        """Получение списка проектов команды"""
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
        """Получение списка участников команды"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT pu.user_id, pu.username, tm.role
                FROM personal_user pu
                JOIN team_member tm ON pu.user_id = tm.user_id
                WHERE tm.team_id = %s
                ORDER BY tm.role DESC, pu.username
            """, (team_id,))
            return cursor.fetchall()  # Возвращаем список кортежей (user_id, username, role)
        except Exception as e:
            print(f"Ошибка при получении списка участников: {e}")
            return []

    def invite_user_to_team(self, team_id: int, email: str) -> bool:
        """Приглашение пользователя в команду"""
        try:
            # Находим пользователя по email
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT user_id FROM personal_user WHERE email = %s
            """, (email,))
            row = cursor.fetchone()
            if not row:
                return False
            
            user_id = row[0]
            
            # Проверяем, не состоит ли уже пользователь в команде
            cursor.execute("""
                SELECT user_id FROM team_member 
                WHERE team_id = %s AND user_id = %s
            """, (team_id, user_id))
            if cursor.fetchone():
                return False
            
            # Добавляем пользователя в команду
            cursor.execute("""
                INSERT INTO team_member (team_id, user_id, role)
                VALUES (%s, %s, 'member')
            """, (team_id, user_id))
            self.connection.commit()
            return True
        except Exception as e:
            print(f"Ошибка при приглашении пользователя: {e}")
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
        """Получение всех задач проекта с учетом статуса"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT task_id, title, description, user_id, status, deadline, 
                       priority, project_id, team_id, notification_time, 
                       notified, created_at
                FROM tasks 
                WHERE project_id = %s
                ORDER BY created_at DESC
            """, (project_id,))
            
            tasks = []
            for row in cursor.fetchall():
                task = Task(
                    title=row[1],
                    description=row[2],
                    user_id=row[3],
                    status=row[4] if row[4] is not None else 1,  # Если статус None, считаем задачу в работе
                    deadline=row[5],
                    priority=row[6],
                    project_id=row[7],
                    team_id=row[8],
                    notification_time=row[9],
                    notified=row[10],
                    created_at=row[11]
                )
                task.task_id = row[0]
                print(f"[DEBUG] Загружена задача {task.task_id} со статусом {task.status}")
                tasks.append(task)
            return tasks
        except Exception as e:
            print(f"[ERROR] Ошибка при получении задач проекта: {e}")
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
        """Создание таблиц"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    task_id SERIAL PRIMARY KEY,
                    title VARCHAR(255) NOT NULL,
                    description TEXT,
                    user_id INTEGER NOT NULL,
                    status BOOLEAN DEFAULT FALSE,
                    deadline TIMESTAMP,
                    priority INTEGER DEFAULT 1,
                    project_id INTEGER,
                    team_id INTEGER,
                    notification_time TIMESTAMP,
                    notified BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            self.connection.commit()
        except Exception as e:
            print(f"Ошибка при создании таблиц: {str(e)}")

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
        except Exception as e:
            print(f"Ошибка при обновлении таблицы tasks: {str(e)}")

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
        """Получение задач пользователя"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT task_id, title, description, deadline, priority,
                       project_id, team_id, user_id, created_at,
                       notification_time, notified, status
                FROM tasks
                WHERE user_id = %s
                ORDER BY created_at DESC
            """, (user_id,))
            tasks = cursor.fetchall()
            return [Task(
                task_id=row[0],
                title=row[1],
                description=row[2],
                deadline=row[3],
                priority=row[4],
                project_id=row[5],
                team_id=row[6],
                user_id=row[7],
                created_at=row[8],
                notification_time=row[9],
                notified=row[10],
                status=row[11]  # 0 - новые, 1 - в работе, 2 - завершенные
            ) for row in tasks]
        except Exception as e:
            print(f"Ошибка при получении задач пользователя: {e}")
            return []

    def update_task_status(self, task_id: int, new_status: int) -> bool:
        """Обновление статуса задачи"""
        try:
            print(f"[DEBUG] Попытка обновить задачу {task_id} на статус {new_status}")
            
            # Проверяем валидность нового статуса
            if new_status not in [0, 1, 2]:
                print(f"[ERROR] Некорректный статус: {new_status}")
                return False
            
            cursor = self.connection.cursor()
            
            # Получаем текущий статус
            cursor.execute("SELECT DISTINCT status FROM tasks WHERE task_id = %s", (task_id,))
            current = cursor.fetchone()
            
            if current is None:
                print(f"[ERROR] Задача {task_id} не найдена")
                return False
            
            print(f"[DEBUG] Текущий статус в БД: {current[0]}")
            
            # Обновляем статус только если он изменился
            if current[0] != new_status:
                cursor.execute("""
                    UPDATE tasks 
                    SET status = %s 
                    WHERE task_id = %s
                    RETURNING task_id, status
                """, (new_status, task_id))
                
                updated = cursor.fetchone()
                self.connection.commit()
                
                success = updated is not None
                print(f"[DEBUG] Статус обновлен успешно: {success}")
                print(f"[DEBUG] Новый статус в БД: {updated[1] if updated else None}")
                return success
            else:
                print("[DEBUG] Статус не изменился, обновление не требуется")
                return True
            
        except Exception as e:
            print(f"[ERROR] Ошибка при обновлении статуса задачи: {e}")
            import traceback
            traceback.print_exc()
            self.connection.rollback()
            return False

    def get_task_status(self, task_id: int) -> int:
        """Получение текущего статуса задачи"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT DISTINCT status FROM tasks WHERE task_id = %s", (task_id,))
            result = cursor.fetchone()
            return result[0] if result else None
        except Exception as e:
            print(f"[ERROR] Ошибка при получении статуса задачи: {e}")
            return None

    def update_task(self, task_id: int, title=None, description=None, 
                    deadline=None, priority=None, status=None, user_id=None, team_id=None) -> bool:
        """Обновление задачи с логированием изменений"""
        try:
            # Получаем текущие данные задачи
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT title, description, deadline, priority, user_id, team_id, status
                FROM tasks WHERE task_id = %s
            """, (task_id,))
            old_data = cursor.fetchone()
            
            if not old_data:
                return False
            
            old_title, old_description, old_deadline, old_priority, old_user_id, old_team_id, old_status = old_data

            # Формируем SQL запрос для обновления
            update_parts = []
            values = []
            
            if title is not None:
                update_parts.append("title = %s")
                values.append(title)
            if description is not None:
                update_parts.append("description = %s")
                values.append(description)
            if deadline is not None:
                update_parts.append("deadline = %s")
                values.append(deadline)
            if priority is not None:
                update_parts.append("priority = %s")
                values.append(int(priority))  # Преобразуем в int
            if status is not None:
                update_parts.append("status = %s")
                values.append(bool(status))  # Преобразуем в bool
            if user_id is not None:
                update_parts.append("user_id = %s")
                values.append(int(user_id))
            if team_id is not None:
                update_parts.append("team_id = %s")
                values.append(int(team_id))
            
            if not update_parts:
                return False
            
            values.append(task_id)
            
            # Выполняем обновление
            cursor.execute(f"""
                UPDATE tasks 
                SET {', '.join(update_parts)}
                WHERE task_id = %s
                RETURNING user_id, team_id
            """, values)
            
            current_ids = cursor.fetchone()
            if current_ids:
                current_user_id, current_team_id = current_ids
            else:
                current_user_id, current_team_id = old_user_id, old_team_id

            # Логируем изменения
            if title is not None and str(title) != str(old_title):
                self.add_task_history(
                    task_id=task_id,
                    user_id=current_user_id,
                    team_id=current_team_id,
                    old_description=str(old_title),
                    new_description=str(title),
                    change_type='update_title'
                )
            
            if description is not None and str(description) != str(old_description):
                self.add_task_history(
                    task_id=task_id,
                    user_id=current_user_id,
                    team_id=current_team_id,
                    old_description=str(old_description),
                    new_description=str(description),
                    change_type='update_description'
                )
            
            if deadline is not None and str(deadline) != str(old_deadline):
                self.add_task_history(
                    task_id=task_id,
                    user_id=current_user_id,
                    team_id=current_team_id,
                    old_deadline=old_deadline,
                    new_deadline=deadline,
                    change_type='update_deadline'
                )
            
            if priority is not None and int(priority) != old_priority:
                self.add_task_history(
                    task_id=task_id,
                    user_id=current_user_id,
                    team_id=current_team_id,
                    old_priority=old_priority,
                    new_priority=int(priority),
                    change_type='update_priority'
                )
            
            if status is not None and bool(status) != old_status:
                self.add_task_history(
                    task_id=task_id,
                    user_id=current_user_id,
                    team_id=current_team_id,
                    old_status=old_status,
                    new_status=bool(status),
                    change_type='update_status'
                )

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

    def get_team_info(self, team_id: int) -> dict:
        """Получение информации о команде"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT team_id, name, description, created_at, icon_path, creator_id
                FROM team
                WHERE team_id = %s
            """, (team_id,))
            row = cursor.fetchone()
            if row:
                return {
                    'team_id': row[0],
                    'name': row[1],
                    'description': row[2],
                    'created_at': row[3],
                    'icon_path': row[4],
                    'creator_id': row[5]
                }
            return None
        except Exception as e:
            print(f"Ошибка при получении информации о команде: {e}")
            return None

    def is_team_admin(self, team_id: int, user_id: int) -> bool:
        """Проверка, является ли пользователь администратором команды"""
        try:
            cursor = self.connection.cursor()
            
            # Сначала проверяем, является ли пользователь создателем команды
            cursor.execute("""
                SELECT 1 FROM team 
                WHERE team_id = %s AND creator_id = %s
            """, (team_id, user_id))
            if cursor.fetchone():
                print(f"Пользователь {user_id} является создателем команды {team_id}")
                return True
            
            # Затем проверяем роль в team_member
            cursor.execute("""
                SELECT 1 FROM team_member 
                WHERE team_id = %s AND user_id = %s AND role = 'admin'
            """, (team_id, user_id))
            result = cursor.fetchone() is not None
            print(f"Пользователь {user_id} {'' if result else 'не '}является администратором команды {team_id}")
            return result
        except Exception as e:
            print(f"Ошибка при проверке прав администратора: {e}")
            return False

    def update_team(self, team_id: int, name: str, description: str) -> bool:
        """Обновление информации о команде"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                UPDATE team
                SET name = %s, description = %s
                WHERE team_id = %s
            """, (name, description, team_id))
            self.connection.commit()
            return True
        except Exception as e:
            print(f"Ошибка при обновлении команды: {e}")
            return False

    def remove_team_member(self, team_id: int, user_id: int) -> bool:
        """Исключение участника из команды"""
        try:
            cursor = self.connection.cursor()
            
            # Проверяем, не является ли пользователь создателем команды
            cursor.execute("""
                SELECT creator_id FROM team WHERE team_id = %s
            """, (team_id,))
            creator_id = cursor.fetchone()[0]
            
            if creator_id == user_id:
                print("Нельзя удалить создателя команды")
                return False
            
            # Удаляем участника из team_member и проверяем результат
            cursor.execute("""
                DELETE FROM team_member
                WHERE team_id = %s AND user_id = %s
                RETURNING user_id
            """, (team_id, user_id))
            
            result = cursor.fetchone()
            if not result:
                print(f"Участник не найден в team_member (team_id={team_id}, user_id={user_id})")
                self.connection.rollback()
                return False
            
            # Проверяем, есть ли записи в user_team
            cursor.execute("""
                SELECT EXISTS (
                    SELECT 1 FROM user_team 
                    WHERE team_id = %s AND user_id = %s
                )
            """, (team_id, user_id))
            
            if cursor.fetchone()[0]:
                cursor.execute("""
                    DELETE FROM user_team
                    WHERE team_id = %s AND user_id = %s
                    RETURNING user_id
                """, (team_id, user_id))
                
                if not cursor.fetchone():
                    print("Ошибка при удалении из user_team")
                    self.connection.rollback()
                    return False
            
            self.connection.commit()
            print(f"Участник успешно удален (team_id={team_id}, user_id={user_id})")
            return True
            
        except Exception as e:
            print(f"Ошибка при исключении участника: {e}")
            import traceback
            traceback.print_exc()
            self.connection.rollback()
            return False

    def get_team_task_stats(self, team_id: int) -> dict:
        """Получение статистики задач команды"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN status = true THEN 1 ELSE 0 END) as completed,
                    SUM(CASE WHEN status = false THEN 1 ELSE 0 END) as in_progress
                FROM tasks
                WHERE team_id = %s
            """, (team_id,))
            row = cursor.fetchone()
            return {
                'total': row[0] or 0,
                'completed': row[1] or 0,
                'in_progress': row[2] or 0
            }
        except Exception as e:
            print(f"Ошибка при получении статистики задач: {e}")
            return {'total': 0, 'completed': 0, 'in_progress': 0}

    def get_team_tasks(self, team_id: int) -> list:
        """Получение всех задач команды"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT task_id, title, description, user_id, status, deadline, 
                       priority, project_id, team_id, notification_time, 
                       notified, created_at
                FROM tasks 
                WHERE team_id = %s
                ORDER BY created_at DESC
            """, (team_id,))
            
            tasks = []
            for row in cursor.fetchall():
                task = Task(
                    title=row[1],
                    description=row[2],
                    user_id=row[3],
                    status=row[4],  # integer status (0, 1, 2)
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
            return tasks
        except Exception as e:
            print(f"Ошибка при получении задач команды: {e}")
            return []

    def get_teams_simple(self, user_id: int) -> list:
        """Получение упрощенного списка команд пользователя (для создания задач)"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT t.team_id, t.name
                FROM team t
                JOIN team_member tm ON t.team_id = tm.team_id
                WHERE tm.user_id = %s
                ORDER BY t.name
            """, (user_id,))
            return cursor.fetchall()
        except Exception as e:
            print(f"Ошибка при получении списка команд: {e}")
            return []

    def update_team_info(self, team_id: int, name: str, description: str) -> bool:
        """Обновление информации о команде"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                UPDATE team 
                SET name = %s, description = %s 
                WHERE team_id = %s
            """, (name, description, team_id))
            self.connection.commit()
            return True
        except Exception as e:
            print(f"Ошибка при обновлении информации о команде: {e}")
            self.connection.rollback()
            return False

    def get_all_tasks(self) -> list:
        """Получение всех задач"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT task_id, title, description, deadline, priority,
                       project_id, team_id, user_id, created_at,
                       notification_time, notified, status
                FROM tasks
                ORDER BY created_at DESC
            """)
            tasks = cursor.fetchall()
            return [Task(
                task_id=row[0],
                title=row[1],
                description=row[2],
                deadline=row[3],
                priority=row[4],
                project_id=row[5],
                team_id=row[6],
                user_id=row[7],
                created_at=row[8],
                notification_time=row[9],
                notified=row[10],
                status=row[11]  # Статус: 0 - новые, 1 - в работе, 2 - завершенные
            ) for row in tasks]
        except Exception as e:
            print(f"Ошибка при получении задач: {e}")
            return []

    def add_task_history(self, task_id: int, user_id: int, team_id: int, 
                        old_status=None, new_status=None,
                        old_priority=None, new_priority=None,
                        old_deadline=None, new_deadline=None,
                        old_description=None, new_description=None,
                        comment_id=None,
                        change_type=None) -> bool:
        """Добавление записи в историю изменений"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                INSERT INTO task_history (
                    task_id, user_id, team_id,
                    old_status, new_status,
                    old_priority, new_priority,
                    old_deadline, new_deadline,
                    old_discription, new_description,
                    comment_id, change_type
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
            """, (
                task_id, user_id, team_id,
                old_status, new_status,
                old_priority, new_priority,
                old_deadline, new_deadline,
                old_description, new_description,
                comment_id, change_type
            ))
            self.connection.commit()
            return True
        except Exception as e:
            print(f"Ошибка при добавлении записи в историю: {e}")
            self.connection.rollback()
            return False

    def get_task_history(self, task_id: int) -> list:
        """Получение истории изменений задачи"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT 
                    th.history_id,
                    th.changed_at,
                    pu.username,
                    th.old_status,
                    th.new_status,
                    th.old_priority,
                    th.new_priority,
                    th.old_deadline,
                    th.new_deadline,
                    th.old_discription,
                    th.new_description,
                    th.change_type
                FROM task_history th
                LEFT JOIN personal_user pu ON th.user_id = pu.user_id
                WHERE th.task_id = %s
                ORDER BY th.changed_at DESC
            """, (task_id,))
            return cursor.fetchall()
        except Exception as e:
            print(f"Ошибка при получении истории задачи: {e}")
            return []

    def get_all_task_history(self, user_id: int) -> list:
        """Получение истории всех задач пользователя"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT 
                    t.title as task_title,
                    th.changed_at,
                    pu.username,
                    th.old_status,
                    th.new_status,
                    th.old_priority,
                    th.new_priority,
                    th.old_deadline,
                    th.new_deadline,
                    th.old_discription,
                    th.new_description,
                    th.change_type
                FROM task_history th
                JOIN tasks t ON th.task_id = t.task_id
                LEFT JOIN personal_user pu ON th.user_id = pu.user_id
                WHERE t.user_id = %s OR th.task_id = 0
                ORDER BY th.changed_at DESC
            """, (user_id,))
            return cursor.fetchall()
        except Exception as e:
            print(f"Ошибка при получении истории задач: {e}")
            return []

    def add_comment(self, task_id: int, user_id: int, text: str) -> bool:
        """Добавление комментария"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                INSERT INTO comment (task_id, user_id, text)
                VALUES (%s, %s, %s)
                RETURNING comment_id
            """, (task_id, user_id, text))
            
            comment_id = cursor.fetchone()[0]
            
            # Логируем добавление комментария
            self.add_task_history(
                task_id=task_id,
                user_id=user_id,
                team_id=None,
                new_description=text,
                comment_id=comment_id,
                change_type='add_comment'
            )
            
            self.connection.commit()
            return True
        except Exception as e:
            print(f"Ошибка при добавлении комментария: {e}")
            self.connection.rollback()
            return False

    def update_comment(self, comment_id: int, new_text: str, user_id: int) -> bool:
        """Обновление комментария"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT text, task_id FROM comment 
                WHERE comment_id = %s
            """, (comment_id,))
            old_data = cursor.fetchone()
            
            if old_data:
                old_text, task_id = old_data
                
                # Логируем изменение комментария
                self.add_task_history(
                    task_id=task_id,
                    user_id=user_id,
                    team_id=None,
                    old_description=old_text,
                    new_description=new_text,
                    comment_id=comment_id,
                    change_type='update_comment'
                )
                
                cursor.execute("""
                    UPDATE comment 
                    SET text = %s 
                    WHERE comment_id = %s
                """, (new_text, comment_id))
                
                self.connection.commit()
                return True
        except Exception as e:
            print(f"Ошибка при обновлении комментария: {e}")
            self.connection.rollback()
            return False

    def delete_comment(self, comment_id: int, user_id: int) -> bool:
        """Удаление комментария"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT text, task_id FROM comment 
                WHERE comment_id = %s
            """, (comment_id,))
            comment_data = cursor.fetchone()
            
            if comment_data:
                text, task_id = comment_data
                
                # Логируем удаление комментария
                self.add_task_history(
                    task_id=task_id,
                    user_id=user_id,
                    team_id=None,
                    old_description=text,
                    change_type='delete_comment'
                )
                
                cursor.execute("""
                    DELETE FROM comment 
                    WHERE comment_id = %s
                """, (comment_id,))
                
                self.connection.commit()
                return True
        except Exception as e:
            print(f"Ошибка при удалении комментария: {e}")
            self.connection.rollback()
            return False

    def get_task_comments(self, task_id: int) -> list:
        """Получение комментариев к задаче"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT 
                    c.comment_id,
                    c.comment_text,
                    c.created_at,
                    pu.username,
                    pu.user_id
                FROM comment c
                JOIN personal_user pu ON c.user_id = pu.user_id
                WHERE c.task_id = %s
                ORDER BY c.created_at DESC
            """, (task_id,))
            return cursor.fetchall()
        except Exception as e:
            print(f"Ошибка при получении комментариев: {e}")
            return []

    def add_comment_to_task(self, task_id: int, user_id: int, comment_text: str) -> bool:
        """Добавление комментария к задаче"""
        try:
            cursor = self.connection.cursor()
            
            # Получаем team_id задачи
            cursor.execute("""
                SELECT team_id FROM tasks WHERE task_id = %s
            """, (task_id,))
            team_id = cursor.fetchone()[0]
            
            # Добавляем комментарий
            cursor.execute("""
                INSERT INTO comment (task_id, user_id, comment_text, created_at)
                VALUES (%s, %s, %s, NOW())
                RETURNING comment_id
            """, (task_id, user_id, comment_text))
            
            comment_id = cursor.fetchone()[0]
            
            # Добавляем запись в историю
            self.add_task_history(
                task_id=task_id,
                user_id=user_id,
                team_id=team_id,
                new_description=comment_text,
                comment_id=comment_id,
                change_type='add_comment'
            )
            
            self.connection.commit()
            return True
        except Exception as e:
            print(f"Ошибка при добавлении комментария: {e}")
            self.connection.rollback()
            return False

   