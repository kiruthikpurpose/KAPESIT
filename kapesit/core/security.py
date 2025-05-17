import hashlib
class SecurityManager:
    def __init__(self):
        self.users = {}
    def add_user(self, username, password):
        self.users[username] = hashlib.sha256(password.encode()).hexdigest()
    def authenticate(self, username, password):
        return self.users.get(username) == hashlib.sha256(password.encode()).hexdigest()
    def has_access(self, username, resource):
        return username in self.users 