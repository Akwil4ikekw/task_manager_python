

class TaskHistory:
    def __init__(self, history_id:int, task_id:int, user_id:int, status:bool, start:str, end:str, changed_at:str, old_status:bool, new_status:bool, old_priority:int, new_priority:int, old_deadline:str, new_deadline:str, team_id:int, comment_id:int):
        self.history_id = history_id

        self.task_id = task_id
        self.changed_at = changed_at
        self.old_status = old_status
        self.new_status = new_status
        self.old_priority = old_priority
        self.new_priority = new_priority
        self.old_deadline = old_deadline
        self.new_deadline = new_deadline
        self.team_id = team_id
        self.comment_id = comment_id
        self.user_id=user_id    
        self.status = status
        self.start = start
        self.end = end

