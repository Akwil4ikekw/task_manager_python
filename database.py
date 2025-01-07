import psycopg2
from typing import List, Optional

class Database:
    def __init__(self, host: str, database: str, user: str, password: str):
        self.connection = psycopg2.connect(
            host="localhost",
            database="Task_manager2.0",
            user="Aquil",
            password="123123"
        )
        self.cursor = self.connection.cursor()


            #Metods for Tasks


    def add_task(self, name: str, id_project: int, id_description: int, date: str, status: str = "backlog") -> None:
        query = """
        INSERT INTO public."Task" (name, id_project, id_description, date, status)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id_task;
        """
        self.cursor.execute(query, (name, id_project, id_description, date, status))
        self.connection.commit()
        print(f"Task added with ID: {self.cursor.fetchone()[0]}")

    def remove_task(self, id_task: int) -> None:
        query = """
        DELETE FROM public."Task"
        WHERE id_task = %s;
        """
        self.cursor.execute(query, (id_task,))
        self.connection.commit()
        print(f"Task with ID {id_task} removed.")

    def update_task_status(self, id_task: int, new_status: str) -> None:
        query = """
        UPDATE public."Task"
        SET status = %s
        WHERE id_task = %s;
        """
        self.cursor.execute(query, (new_status, id_task))
        self.connection.commit()
        print(f"Task {id_task} updated to status '{new_status}'.")

 
 
    def add_task_history(self, id_task: int, old_status: str, new_status: str) -> None:
        query = """
        INSERT INTO public."TaskHistory" (id_task, old_status, new_status)
        VALUES (%s, %s, %s);
        """
        self.cursor.execute(query, (id_task, old_status, new_status))
        self.connection.commit()
        print(f"Task history updated for Task ID {id_task}: {old_status} -> {new_status}.")

    def add_task_status(self, status_name: str, description: Optional[str] = None) -> int:
        query = """
        INSERT INTO public."TaskStatus" (status_name, description)
        VALUES (%s, %s)
        RETURNING id_status;
        """
        self.cursor.execute(query, (status_name, description))
        self.connection.commit()
        id_status = self.cursor.fetchone()[0]
        print(f"Task status '{status_name}' added with ID: {id_status}")
        return id_status

    def close(self):
        self.cursor.close()
        self.connection.close()

    
    def get_task_by_id(self, id_task: int) -> Optional[dict]:
        query = """
        SELECT id_task, name, date, status, id_project, id_description
        FROM public."Task"
        WHERE id_task = %s;
        """
        self.cursor.execute(query, (id_task,))
        row = self.cursor.fetchone()
        if row:
            return {
                'id_task': row[0], 'name': row[1], 'date': row[2], 'status': row[3],
                'id_project': row[4], 'id_description': row[5]
            }
        return None
    
    def get_description_by_id(self, id_description: int) -> Optional[dict]:
        query = """
        SELECT id_description, description
        FROM public."Description"
        WHERE id_description = %s;
        """
        self.cursor.execute(query, (id_description,))
        row = self.cursor.fetchone()
        if row:
            return {'id_description': row[0], 'description': row[1]}
        return None
    







    def get_all_projects(self) -> List[dict]:
        query = """
        SELECT id_project, name, id_description
        FROM public."Project";
        """
        self.cursor.execute(query)
        projects = self.cursor.fetchall()
        return [{'id_project': row[0], 'name': row[1], 'id_description': row[2]} for row in projects]

    def get_project_by_id(self, id_project: int) -> Optional[dict]:
        query = """
        SELECT id_project, name, id_description
        FROM public."Project"
        WHERE id_project = %s;
        """
        self.cursor.execute(query, (id_project,))
        row = self.cursor.fetchone()
        if row:
            return {'id_project': row[0], 'name': row[1], 'id_description': row[2]}
        return None

    def get_projects_with_descriptions(self) -> List[dict]:
        query = """
        SELECT p.id_project, p.name, d.description
        FROM public."Project" p
        LEFT JOIN public."Description" d ON p.id_description = d.id_description;
        """
        self.cursor.execute(query)
        projects = self.cursor.fetchall()
        return [{'id_project': row[0], 'name': row[1], 'description': row[2]} for row in projects]

    # Example usage:






    def remove_project(self, id_project: int) -> None:
        query = """
        DELETE FROM public."Project"
        WHERE id_project = %s;
        """
        self.cursor.execute(query, (id_project,))
        self.connection.commit()
        print(f"Project with ID {id_project} removed.")







    def add_project(self, name: str, id_description: Optional[int] = None) -> None:
        query = """
        INSERT INTO public."Project" (name, id_description)
        VALUES (%s, %s)
        RETURNING id_project;
        """
        self.cursor.execute(query, (name, id_description))
        self.connection.commit()
        print(f"Project added with ID: {self.cursor.fetchone()[0]}")


    
    def remove_project(self, id_project: int) -> None:
        query = """
        DELETE FROM public."Project"
        WHERE id_project = %s;
        """
        self.cursor.execute(query, (id_project,))
        self.connection.commit()
        print(f"Project with ID {id_project} removed.")






    

    def add_description(self, description: str) -> int:
        query = """
        INSERT INTO public."Description" (description)
        VALUES (%s)
        RETURNING id_description;
        """
        self.cursor.execute(query, (description,))
        self.connection.commit()
        id_description = self.cursor.fetchone()[0]
        print(f"Description added with ID: {id_description}")
        return id_description
