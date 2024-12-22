from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy_utils import URLType

from db.annotate import created_at, str_255, updated_at
from db.models import Base

if TYPE_CHECKING:
    from .brand import Brand
    from .character import Character
    from .type_product import TypeProduct


class Product(Base):
    """Модель для продукта компании."""

    alt_table_name = "Продукция"

    MODEL = "Модель"
    TYPEPRODUCT = "Тип продукции"
    BRAND = "Бренд"
    DIMENSIONS = "Габариты"
    DESCRIPTION = "Описание"
    PRICE = "Цена"
    POWER = "Мощность"
    VIEW = "Количество просмотров"
    PDF = "Ссылка на pdf"
    IMG = "Ссылка на img"
    CREATE = "Дата создания"
    UPDATE = "Дата изменения"
    CHARACTER = "Характеристики"

    model: Mapped[str_255]
    character: Mapped[list["Character"]] = relationship(
        secondary="product_character_association",
        back_populates="product",
    )
    typeproduct_id: Mapped[int] = mapped_column(ForeignKey("typeproduct.id"))
    typeproduct: Mapped["TypeProduct"] = relationship(
        back_populates="product", lazy="selectin"
    )

    brand_id: Mapped[int] = mapped_column(ForeignKey("brand.id"))
    brand: Mapped["Brand"] = relationship(
        back_populates="product", lazy="selectin"
    )

    dimensions: Mapped[str]
    description: Mapped[str] = mapped_column(
        Text,
        default="",
        server_default="",
    )
    price: Mapped[int | None]
    power: Mapped[float | None]
    view_stats: Mapped[int | None]
    pdf_url: Mapped[str] = mapped_column(URLType)
    image_url: Mapped[str] = mapped_column(URLType)
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]

    @classmethod
    def get_field_names(cls):
        """Поля модели."""
        return [
            cls.MODEL,
            cls.TYPEPRODUCT,
            cls.BRAND,
            cls.DIMENSIONS,
            cls.DESCRIPTION,
            cls.PRICE,
            cls.POWER,
            cls.VIEW,
            cls.PDF,
            cls.IMG,
            cls.CREATE,
            cls.UPDATE,
            cls.CHARACTER,
        ]

    def __repr__(self):
        return (
            f"{self.typeproduct}, модель - {self.model},"
            f" бренд - {self.brand.name}, "
            f"цена - {self.price}, характеристики: {self.character}, "
            f"описание - {self.description[:20]}..."
        )
