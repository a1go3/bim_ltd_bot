import asyncio

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from db.core import async_session_factory
from db.models import (
    Brand,
    Character,
    Product,
    ProductCharacterAssociation,
    TypeProduct,
)


async def insert_brand_character():
    """Внесение в бд списка типов продуктов и брендов."""
    async with async_session_factory() as session:

        product_type1 = TypeProduct(name="Кондиционер")

        brand1 = Brand(name="Samsung")
        brand2 = Brand(name="Toshiba")
        brand3 = Brand(name="LG")

        character1 = Character(name="Домашний")
        character2 = Character(name="Промышленный")
        character3 = Character(name="Настенный")
        character4 = Character(name="Инверторный")

        session.add_all(
            [
                product_type1,
                brand1,
                brand2,
                brand3,
                character1,
                character2,
                character3,
                character4,
            ]
        )
        await session.commit()


async def insert_product():
    """Внесение в бд продукта."""
    async with async_session_factory() as session:
        product1 = Product(
            model="SBHXGH123",
            brand_id=1,
            typeproduct_id=1,
            dimensions="150х60х40",
            description="хороший",
            price=10000,
            pdf_url="https://smallpdf.com/ru/file#s=280e94ab-"
            "85eb-4ce0-bd07-dde3292b608b",
            image_url="https://images.unsplash.com/photo-"
            "1617861648989-76a572012089?q=80&w=3270&auto=format&fit"
            "=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwa"
            "G90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
            power=0.2,
        )
        product2 = Product(
            model="LKM890YT",
            brand_id=2,
            typeproduct_id=1,
            dimensions="15х6х40",
            description="Нормальный",
            price=100000,
            pdf_url="https://smallpdf.com/ru/file#s="
            "79fcfeab-ac7e-443a-ae7d-be8eda8e6664",
            image_url="https://images.unsplash.com/photo-"
            "1590756254933-2873d72a83b6?q=80&w=3270&auto=format&fit"
            "=crop&ixlib=rb-4.0.3&ixid"
            "=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
            power=1.7,
        )

        product3 = Product(
            model="LKIYT67",
            brand_id=3,
            typeproduct_id=1,
            dimensions="30х20х40",
            description="Прекрасный",
            price=50000,
            pdf_url="https://smallpdf.com/ru/file#s=8456a996-d7c9"
            "-46e5-8c40-ffec43ba65e5",
            image_url="https://plus.unsplash.com/premium_photo-"
            "1661315526732-271aa84f480d?q=80&w=3270&auto=format&fit"
            "=crop&ixlib=rb-4.0.3&ixid"
            "=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
            power=2.7,
        )

        product4 = Product(
            model="LOIKJG54",
            brand_id=2,
            typeproduct_id=1,
            dimensions="60х30х70",
            description="Замечательный",
            price=500000,
            pdf_url="https://smallpdf.com/ru/file#s=964af8d3-0c12-43e0-843e"
            "-87fb616f2d23",
            image_url="https://plus.unsplash.com/premium_photo-1679943423706"
            "-570c6462f9a4?q=80&w=3105&auto=format&fit=crop&ixlib=rb"
            "-4.0.3&ixid"
            "=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
            power=3.0,
        )

        session.add_all([product1, product2, product3, product4])
        await session.commit()

        products = await session.execute(select(Product))
        product_id = products.scalars().first().id

        characters = await session.execute(select(Character))
        all_characters_from_db = characters.scalars().all()

        characters1_id = all_characters_from_db[0].id
        characters2_id = all_characters_from_db[1].id

        product_character1 = ProductCharacterAssociation(
            product_id=product_id, character_id=characters1_id
        )
        product_character2 = ProductCharacterAssociation(
            product_id=product_id, character_id=characters2_id
        )
        session.add_all([product_character1, product_character2])

        await session.commit()


async def get_product():
    """Функция для тестирования. Выводит на экран Product."""
    async with async_session_factory() as session:
        stmt = await session.execute(
            select(Product).options(selectinload(Product.character))
        )
        products = stmt.scalars().all()
        print(products[0])
        print(products[1])


if __name__ == "__main__":
    asyncio.run(insert_brand_character())
    asyncio.run(insert_product())
    asyncio.run(get_product())
