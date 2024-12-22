from sqlalchemy import String
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    declared_attr,
    mapped_column,
)

from ..annotate import str_255


class Base(DeclarativeBase):
    """Базовая модель проекта."""

    __table_args__ = {"extend_existing": True}
    type_annotation_map = {str_255: String(255)}

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    id: Mapped[int] = mapped_column(primary_key=True)
