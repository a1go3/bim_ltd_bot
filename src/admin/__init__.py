import asyncio
import logging

from flask import Flask, g

from db.models import Brand, Character, Product, TypeProduct, User
from .settings import Config

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config.from_object(Config)


async def fetch_type_products():  # noqa
    user = User.__tablename__, User.alt_table_name
    type_product = TypeProduct.__tablename__, TypeProduct.alt_table_name
    product = Product.__tablename__, Product.alt_table_name
    brand = Brand.__tablename__, Brand.alt_table_name
    character = Character.__tablename__, Character.alt_table_name
    return (
        user,
        product,
        brand,
        character,
        type_product,
    )


@app.before_request
def before_request():  # noqa
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    (g.user, g.product, g.brand, g.character, g.type_product) = (
        loop.run_until_complete(fetch_type_products())
    )
    loop.close()


@app.context_processor
def inject_type_products():  # noqa
    return dict(
        tables=(g.user, g.product, g.brand, g.character, g.type_product),
    )


from . import (  # noqa
    brand_views,
    character_views,
    login_views,
    product_views,
    typeproduct_views,
    user_views,
)
