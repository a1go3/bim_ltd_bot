from flask import flash, redirect, render_template, request
from flask import session as s
from flask import url_for
from sqlalchemy.future import select

from admin import app
from db.core import get_async_session
from db.models import User

from .permission import requires_permission


@app.route("/")
async def index():
    """Страница перехода на вход."""
    return redirect(url_for("login"))


@app.route("/admin", methods=["GET"])
@requires_permission("view")
async def home():
    """Домашняя страница."""
    return render_template(
        "index.html",
    )


@app.route("/admin/login", methods=["GET", "POST"])
async def login():
    """Вход в административную панель."""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        async for session in get_async_session():
            result = await session.execute(
                select(User).filter_by(login=username)
            )
            user = result.scalar_one_or_none()
            if user and await user.check_password(password):
                s["user_id"] = user.id
                return redirect(url_for("home"))
        flash("Неверный логин или пароль", "danger")
        return redirect(url_for("login"))
    return render_template("login.html")


@app.route("/admin/logout", methods=["GET", "POST"])
async def logout():
    """Выход."""
    s.pop("user_id", None)
    flash("Вы успешно вышли из системы.", "success")
    return redirect(url_for("login"))
