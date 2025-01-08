class User:
    def __init__(self, user_id:int, name:str, email:str, password:str, created_at:str, status:bool):
        self.user_id = user_id
        self.name = name
        self.email = email
        self.password = password
        self.created_at = created_at
        self.status = status

