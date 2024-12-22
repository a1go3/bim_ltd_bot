from http import HTTPStatus

from flask import render_template

from db.core import get_async_session

from . import app


class InvalidAdminUsage(Exception):
    """Класс для обработки исключений."""

    status_code = HTTPStatus.BAD_REQUEST

    def __init__(self, message, status_code=None):
        """Инициализация."""
        super().__init__()
        self.message = message
        if status_code is not None:
            self.status_code = status_code


@app.errorhandler(InvalidAdminUsage)
def invalid_admin_usage(error):
    """Общие ошибки."""
    context = {"error_message": error.message}
    return render_template("error.html", **context), HTTPStatus.NOT_FOUND


@app.errorhandler(404)
def page_not_found(error):
    """Страница не найдена."""
    return render_template("404.html"), HTTPStatus.NOT_FOUND


@app.errorhandler(500)
async def internal_error(error):
    """Ошибки сервера."""
    async for session in get_async_session():
        session.rollback()
    return render_template("500.html"), HTTPStatus.INTERNAL_SERVER_ERROR
