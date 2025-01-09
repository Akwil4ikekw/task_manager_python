from datetime import datetime

class Team:
    def __init__(self, team_name: str, description: str = None, team_id: int = None):
        self.team_id = team_id
        self.team_name = team_name
        self.description = description
        self.created_at = datetime.now()

# class TeamNotification:
#     def __init__(self, notification_id: int = None, team_id: int = None, 
#                  user_id: int = None, message: str = None, 
#                  notification_type: str = None, is_read: bool = False):
#         self.notification_id = notification_id
#         self.team_id = team_id
#         self.user_id = user_id
#         self.message = message
#         self.notification_type = notification_type
#         self.is_read = is_read
#         self.created_at = datetime.now()
    