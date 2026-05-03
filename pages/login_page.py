from .base_page import BasePage

class LoginPage(BasePage):
    def __init__(self):
        super().__init__()
        self.registered_users = {"admin": "password123"}

    def login(self, username, password):
        if username in self.registered_users and self.registered_users[username] == password:
            self.log_action(f"User '{username}' logged in successfully.")
            return True
        self.log_action("Login failed: Invalid credentials.")
        return False