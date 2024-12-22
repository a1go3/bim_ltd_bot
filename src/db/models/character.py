from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, relationship

from db.annotate import str_255
from db.models import Base

if TYPE_CHECKING:
    from .product import Product


class Character(Base):
    """Модель для характеристик продуктов."""

    alt_table_name = "Характеристики"
    NAME = "Характеристика"

    name: Mapped[str_255]
    product: Mapped[list["Product"]] = relationship(
        secondary="product_character_association",
        back_populates="character",
    )

    @classmethod
    def get_field_names(cls):
        """Поля модели."""
        return [cls.NAME]

    def __repr__(self):
        return f"{self.name}"
