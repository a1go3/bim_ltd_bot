from http import HTTPStatus

from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from db.core import get_async_session
from db.models import Brand, Character, Product, TypeProduct

from .error_hendlers import InvalidAdminUsage

NULL_PRICE = 0


class CRUDBase:
    """Базовый класс для CRUD операций."""

    def __init__(self, model):
        """Инициализация."""
        self.model = model

    async def get_object_list(self):
        """Возвращает список объектов из БД."""
        async for session in get_async_session():
            object_list = await session.execute(select(self.model))
            object_list = object_list.scalars().all()
            return object_list

    async def check_object_uniq(self, uniq_field_value):
        """Проверяет объект из БД на уникальность."""
        async for session in get_async_session():
            db_object = await session.execute(
                select(self.model).where(self.model.name == uniq_field_value)
            )
            db_object = db_object.scalars().first()
            if db_object:
                raise InvalidAdminUsage(
                    f"Объект с названием {uniq_field_value} уже существует"
                )

    async def delete_object(self, id):
        """Удаляет объект из БД."""
        async for session in get_async_session():
            db_object = await session.execute(
                select(self.model).where(self.model.id == id)
            )
            db_object = db_object.scalars().first()
            if not db_object:
                raise InvalidAdminUsage(
                    "Указанный объект не найден", HTTPStatus.NOT_FOUND
                )
            await session.delete(db_object)
            await session.commit()

    async def add_object(self, form_data):
        """Добавляет объект в БД."""
        async for session in get_async_session():
            await self.check_object_uniq(form_data["name"])
            db_object = self.model(**form_data)
            session.add(db_object)
            await session.commit()

    async def edit_object(self, form_data, id):
        """Редактирует объект в БД."""
        async for session in get_async_session():
            db_object = await session.execute(
                select(self.model).where(self.model.id == id)
            )
            db_object = db_object.scalars().first()
            for field in db_object.__table__.columns:
                if field.name in form_data:
                    setattr(db_object, field.name, form_data[field.name])
            await session.commit()


crud_brand = CRUDBase(Brand)
crud_character = CRUDBase(Character)
crud_typeproduct = CRUDBase(TypeProduct)


class CRUDProduct(CRUDBase):
    """Базовый класс для CRUD операций с моделью Product."""

    async def check_object_uniq(self, uniq_field_value):
        """Проверяет объект из БД на уникальность."""
        async for session in get_async_session():
            db_object = await session.execute(
                select(self.model).where(self.model.model == uniq_field_value)
            )
            db_object = db_object.scalars().first()
            if db_object:
                raise InvalidAdminUsage(
                    f"Объект с названием {uniq_field_value} уже существует"
                )

    async def get_object_list(self):
        """Возвращает список объектов из БД со связанными объектами."""
        async for session in get_async_session():
            object_list = await session.execute(
                select(Product).options(selectinload(Product.character))
            )
            object_list = object_list.scalars().all()
            return object_list

    async def add_object(self, form_data, through_model, characters_data):
        """Добавляет объект в БД со связанными объектами."""
        async for session in get_async_session():
            await self.check_object_uniq(form_data["model"])
            if "brand_id" not in form_data:
                raise InvalidAdminUsage("Не указан бренд!")
            form_data["brand_id"] = int(form_data["brand_id"])
            if "typeproduct_id" not in form_data:
                raise InvalidAdminUsage("Не указан тип продукта!")
            form_data["typeproduct_id"] = int(form_data["typeproduct_id"])
            if form_data["price"]:
                form_data["price"] = int(form_data["price"])
            if not form_data["price"]:
                form_data["price"] = NULL_PRICE
            form_data["power"] = float(form_data["power"])
            if "character_id" in form_data:
                form_data.pop("character_id")
            product = self.model(**form_data)
            session.add(product)
            await session.commit()
            await session.refresh(product)
            if characters_data:
                for character in characters_data:
                    product_character = through_model(
                        product_id=product.id, character_id=int(character)
                    )
                    session.add(product_character)
            await session.commit()

    async def edit_object(self, form_data, id, through_model, characters_data):
        """Редактирует объект в БД со связанными объектами."""
        async for session in get_async_session():
            product = await session.execute(
                select(self.model)
                .where(self.model.id == id)
                .options(selectinload(self.model.character))
            )
            product = product.scalars().first()
            if not product:
                raise InvalidAdminUsage(
                    "Указанный объект не найден", HTTPStatus.NOT_FOUND
                )
            if "character_id" in form_data:
                form_data.pop("character_id")
            correct_data = {}
            for key, value in form_data.items():
                if value:
                    correct_data[key] = value
            if "brand_id" in correct_data:
                correct_data["brand_id"] = int(correct_data["brand_id"])
            if "typeproduct_id" in correct_data:
                correct_data["typeproduct_id"] = int(
                    correct_data["typeproduct_id"]
                )
            if "price" in correct_data:
                correct_data["price"] = int(correct_data["price"])
            if "power" in correct_data:
                correct_data["power"] = float(correct_data["power"])
            for field in product.__table__.columns:
                if field.name in correct_data:
                    setattr(product, field.name, correct_data[field.name])
            if characters_data:
                characters_data = [
                    int(character) for character in characters_data
                ]
                product_character_id = [
                    character.id for character in product.character
                ]
                for character in product_character_id:
                    if character not in characters_data:
                        product_character = await session.execute(
                            select(through_model).filter(
                                through_model.product_id == product.id,
                                through_model.character_id == int(character),
                            )
                        )
                        product_character = product_character.scalars().first()
                        await session.delete(product_character)
                for character in characters_data:
                    if character not in product_character_id:
                        product_character = through_model(
                            product_id=product.id, character_id=int(character)
                        )
                        session.add(product_character)
            await session.commit()


crud_product = CRUDProduct(Product)
