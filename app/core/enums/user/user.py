from enum import Enum 

class UserRole(str, Enum):
    ADMIN = "ADMIN"
    USER = "USER"
    
class AuthProvider(str, Enum):
    LOCAL = "LOCAL"
    GOOGLE = "GOOGLE"
    GITHUB = "GITHUB"
    