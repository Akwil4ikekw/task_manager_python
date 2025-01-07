from typing import List,int,str
from database import Database


class Task:
    def __init__(self, name:str, description:str, status:str, deadline:str, start:str, end:str, project_id:int, task_id:int, hashtags:List[str],priority:int):
        self.name = name
        self.description = description


        self.status = status

        self.deadline = deadline
        self.start = start
        self.end = end

        self.project_id = project_id
        self.task_id = task_id
        self.hashtags = hashtags
        self.priority = priority

        self.db = Database()
    
    def add_task(self):
        
        # Добавляем задачу
        self.id = self.db.add_task(self)

        # Обработка хэштегов
        if self.hashtags:
            for hashtag in self.hashtags:
                self.db.add_task_hashtag(self.id, hashtag)

    def remove_task(self):
    
        if self.id:
            self.db.remove_task(self.id)

    def update_task(self, **kwargs):
        self.db.update_task(self.id, **kwargs)

    def __repr__(self):
        return f"<Task: {self.name}, Status: {self.status}, Priority: {self.priority}, Hashtags: {self.hashtags}>"
