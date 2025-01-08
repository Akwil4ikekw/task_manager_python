

class Team:
    def __init__(self, team_id:int, name:str,created_at:str, updated_at:str, deleted_at:str, status:bool, user_id:int, project_id:int, task_id:int, comment_id:int):
        self.team_id = team_id
        self.name = name
        self.created_at = created_at
    