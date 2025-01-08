class Project:
    def __init__(self, project_id:int, name:str, description:str, created_at:str, team_id:int):
        self.project_id = project_id
        self.name = name
        self.description = description
        self.created_at = created_at
        self.team_id = team_id
