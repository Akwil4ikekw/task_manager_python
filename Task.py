# from typing import int,str,bool
# from database import Database


class Task:
    def __init__(self, title: str, description: str, user_id: int, status: bool, 
                 deadline: float, created_at: float, end: float = None, team_id: int = None, 
                 project_id: int = None, task_id: int = None, priority: int = 1,
                 notification_time: float = None, notified: bool = False):
        self.title = title
        self.description = description
        self.user_id = user_id
        self.status = status
        self.deadline = deadline
        self.created_at = created_at
        self.end = end
        self.team_id = team_id
        self.project_id = project_id
        self.task_id = task_id
        self.priority = priority
        self.notification_time = notification_time if notification_time is not None else deadline
        self.notified = notified
    