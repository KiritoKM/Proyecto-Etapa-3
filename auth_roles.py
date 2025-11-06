from dataclasses import dataclass
from typing import Optional

@dataclass
class User:
    username: str
    role: str  # 'admin' or 'user'

# Base de usuarios en memoria
_USERS_DB = {
    "admin": ("password", "admin"),
    "lucio": ("1234", "user"),
    "camilo": ("abcd", "user"),
}


def authenticate(username: str, password: str) -> Optional[User]:
    if not username:
        return None
    entry = _USERS_DB.get(username)
    if not entry:
        return None
    stored_pw, role = entry
    if password == stored_pw:
        return User(username=username, role=role)
    return None


def is_admin(user: Optional[User]) -> bool:
    return user is not None and user.role == "admin"
