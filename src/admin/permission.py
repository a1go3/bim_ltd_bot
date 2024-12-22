from functools import wraps

from flask import flash, redirect
from flask import session as s
from flask import url_for
from sqlalchemy.future import select

from db.core import get_async_session
from db.models import User


def requires_permission(permission):
    """Декоратор для проверки доступа пользователя."""

    def decorator(f):
        @wraps(f)
        async def decorated_function(*args, **kwargs):
            user_id = s.get("user_id")
            if user_id is None:
                flash(
                    "Вы должны войти в систему для доступа к этой странице.",
                    "danger",
                )
                return redirect(url_for("login"))
            async for session in get_async_session():
                result = await session.execute(
                    select(User).where(User.id == user_id)
                )
                user = result.scalar_one_or_none()
                if user is None or not await user.has_permission(permission):
                    flash("У вас недостаточно прав доступа.", "danger")
                    return redirect(url_for("home"))
            if "user" in f.__code__.co_varnames:
                kwargs["user"] = user
            return await f(*args, **kwargs)

        return decorated_function

    return decorator
