import logging

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import Product

logger = logging.getLogger(__name__)


async def increment_view_stats(
    session: AsyncSession, product_id: int, model=Product
):
    """
    Асинхронно увеличивает счетчик просмотров на 1.

    :param session: Асинхронная сессия базы данных.
    :param model: модель (таблица) в которой есть счетчик кликов,
    по умолчанию таблица Products
    :param product_id: id нужной записи в таблице, используется как
    идентификатор для блокировки.
    """
    # Блокировка с помощью pg_advisory_xact_lock

    await session.execute(text(f"SELECT pg_advisory_xact_lock({product_id})"))
    logger.info(f"Блокировка установлена для продукта с ID: {product_id}")

    # Получение продукта по id
    stmt = select(model).where(model.id == product_id)
    result = await session.execute(stmt)
    product = result.scalar_one_or_none()

    if product:
        # Увеличиваем счетчик просмотров
        if not product.view_stats:
            product.view_stats = 0
        product.view_stats += 1
        await session.commit()
        logger.info(
            f"Счетчик просмотров для продукта с ID {product_id} "
            "увеличен на 1."
        )
    else:
        logger.warning(f"Продукт с ID {product_id} не найден.")
