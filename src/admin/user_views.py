from flask import flash, redirect, render_template, request, url_for
from sqlalchemy.future import select

from db.core import get_async_session
from db.models import User, UserRoleType

from . import app
from .permission import requires_permission


@app.route("/admin/users")
@requires_permission("view")
async def user_list_view():
    """Список пользователей."""
    async for session in get_async_session():
        user_list = await session.execute(select(User))
        user_list = user_list.scalars().all()
    context = {
        "table": User,
        "object_list": user_list,
    }
    return render_template("user.html", **context)


@app.route("/admin/user_add", methods=["POST"])
@requires_permission("create_user")
async def user_add_view(user):
    """Добавление пользователя."""
    username = request.form["username"]
    password = request.form["password"]
    role = request.form["role"]
    user_role = UserRoleType(role)
    async for session in get_async_session():
        new_user = User(login=username, role=user_role)
        await new_user.set_password(password)
        session.add(new_user)
        await session.commit()
    return redirect(url_for("user_list_view"))


@app.route("/admin/user_delete/<int:user_id>", methods=["POST"])
@requires_permission("delete")
async def user_delete_view(user, user_id):
    """Удаление пользователя."""
    async for session in get_async_session():
        user = await session.execute(select(User).where(User.id == user_id))
        user = user.scalar_one_or_none()
        if user:
            await session.delete(user)
            await session.commit()
    return redirect(url_for("user_list_view"))


@app.route("/admin/change_password/<int:user_id>", methods=["POST"])
@requires_permission("edit_user")
async def change_password_view(user, user_id):
    """Изменение пароля пользователя."""
    new_password = request.form["new_password"]
    async for session in get_async_session():
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if user:
            await user.set_password(new_password)
            await session.commit()

    flash("Пароль успешно изменен.", "success")
    return redirect(url_for("user_list_view"))
