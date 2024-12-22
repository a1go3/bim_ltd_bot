import asyncio

import click

from db.models import User, UserRoleType


@click.command()
@click.argument("username")
@click.argument("password")
def create_user(username, password):
    """Команда для создания суперпользователя с указанным логином и паролем."""

    async def async_create_user():
        await User.create_user(username, password, role=UserRoleType.SUPERUSER)
        print(f"Суперпользователь {username} успешно создан.")

    asyncio.run(async_create_user())


if __name__ == "__main__":
    create_user()
