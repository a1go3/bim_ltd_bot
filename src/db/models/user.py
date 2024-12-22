from enum import Enum as PyEnum

import bcrypt
from sqlalchemy import Enum, String
from sqlalchemy.orm import Mapped, mapped_column

from db.core import get_async_session
from db.models import Base


class UserRoleType(PyEnum):
    """Перечисление для ролей пользователей."""

    SUPERUSER = "superuser"
    EDITOR_ROLE = "editor_role"
    REGULAR = "regular"


ROLE_PERMISSIONS = {
    UserRoleType.SUPERUSER: [
        "create",
        "edit",
        "delete",
        "view",
        "create_user",
        "edit_user",
    ],
    UserRoleType.EDITOR_ROLE: ["create", "edit", "view"],
    UserRoleType.REGULAR: ["view"],
}


class User(Base):
    """Модель пользователя."""

    alt_table_name = "Пользватели"
    LOGIN = "Логин"
    ROLE = "Роль"

    login: Mapped[str] = mapped_column(String(25), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String)
    role: Mapped[UserRoleType] = mapped_column(
        Enum(UserRoleType), nullable=False, default=UserRoleType.REGULAR
    )

    async def set_password(self, password: str):
        """Метод для установки пароля."""
        salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(password.encode(), salt).decode()

    async def check_password(self, password: str) -> bool:
        """Метод для проверки пароля."""
        return bcrypt.checkpw(password.encode(), self.password_hash.encode())

    async def has_permission(self, permission: str) -> bool:
        """Проверка, имеет ли пользователь определенные права."""
        permissions = ROLE_PERMISSIONS.get(self.role, [])
        return permission in permissions

    @classmethod
    def get_field_names(cls):  # noqa
        return [
            cls.LOGIN,
            cls.ROLE,
        ]

    @classmethod
    async def create_user(
        cls,
        username: str,
        password: str,
        role: UserRoleType = UserRoleType.EDITOR_ROLE,
    ):
        """Метод для создания пользователя в базе данных."""
        async for session in get_async_session():
            new_user = cls(login=username, role=role)
            await new_user.set_password(password)
            session.add(new_user)
            await session.commit()
