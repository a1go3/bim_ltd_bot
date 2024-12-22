from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, relationship

from db.annotate import str_255
from db.models import Base

if TYPE_CHECKING:
    from .product import Product


class Brand(Base):
    """Модель для хранения брендов."""

    alt_table_name = "Бренды"
    NAME = "Бренд"

    name: Mapped[str_255]
    product: Mapped[list["Product"]] = relationship(
        back_populates="brand",
    )

    @classmethod
    def get_field_names(cls):  # noqa
        return [
            cls.NAME,
        ]

    def __repr__(self):
        return f"Бренд - {self.name}"
