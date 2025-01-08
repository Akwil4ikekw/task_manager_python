from typing import int,str,bool
from database import Database


class Task:
    def __init__(self, name:str,user_id:int, description:str, status:bool, deadline:str, start:str, end:str, team_id:int, project_id:int, task_id:int,priority:int):
        self.name = name
        self.description = description


        self.status = status

        self.deadline = deadline
        self.start = start
        self.end = end
        self.team_id = team_id
        self.project_id = project_id
        self.task_id = task_id
        self.user_id = user_id
        self.priority = priority
        self.db = Database()
    