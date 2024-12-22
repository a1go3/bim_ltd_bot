from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, relationship

from db.annotate import str_255
from db.models import Base

if TYPE_CHECKING:
    from .product import Product


class TypeProduct(Base):
    """Модель для типов продуктов компании."""

    alt_table_name = "Типы продукции"
    NAME = "Тип продукции"

    name: Mapped[str_255]
    product: Mapped[list["Product"]] = relationship(
        back_populates="typeproduct",
    )

    @classmethod
    def get_field_names(cls):
        """Поля модели."""
        return [cls.NAME]

    def __repr__(self):
        return f"Продукт - {self.name}"
