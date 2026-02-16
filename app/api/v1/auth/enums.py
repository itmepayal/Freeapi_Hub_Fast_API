import enum

class UserRole(str, enum.Enum):
    USER = "user"
    ADMIN = "admin"


class LoginType(str, enum.Enum):
    EMAIL_PASSWORD = "email_password"
    GOOGLE = "google"
    GITHUB = "github"
