from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from db.models import Base


class ProductCharacterAssociation(Base):
    """Модель, связывающая продукты и характеристики."""

    __tablename__ = "product_character_association"
    __table_args__ = (
        UniqueConstraint(
            "product_id",
            "character_id",
            name="idx_unique_product_character",
        ),
    )

    product_id: Mapped[int] = mapped_column(ForeignKey("product.id"))
    character_id: Mapped[int] = mapped_column(ForeignKey("character.id"))
