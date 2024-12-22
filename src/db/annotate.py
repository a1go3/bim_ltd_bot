import datetime
from typing import Annotated

from sqlalchemy import text
from sqlalchemy.orm import mapped_column


def utc_now():
    """Функция-помощник для поля updated_at."""
    return datetime.datetime.now(datetime.UTC).replace(tzinfo=None)


created_at = Annotated[
    datetime.datetime,
    mapped_column(server_default=text("TIMEZONE('utc', now())")),
]

updated_at = Annotated[
    datetime.datetime,
    mapped_column(
        server_default=text("TIMEZONE('utc', now())"),
        onupdate=utc_now(),
    ),
]

str_255 = Annotated[str, 255, mapped_column(nullable=False, unique=True)]
