from db.models import Brand, Character, Product, TypeProduct

# Этапы диалога
(
    SELECT_CATEGORY,
    SELECT_TYPE,
    SELECT_POWER,
    SELECT_BRAND,
    SELECT_MODEL,
    SHOW_RESULT,
) = range(6)

FILTER_STEPS_DATA = {
    1: {
        "query_fields": [TypeProduct.id, TypeProduct.name],
        "button_fields": ["callback_data", "label"],
        "group_fields": [TypeProduct.id],
        "order_fields": [TypeProduct.name],
        "join_fields": [Product.typeproduct],
        "where_field": TypeProduct.name,
        "by_range": False,
        "range": 0,
        "range_step": 0,
        "digits_after_dot": 0,
        "message_text": "Выберите тип оборудования",
    },
    2: {
        "query_fields": [Character.id, Character.name],
        "button_fields": ["callback_data", "label"],
        "group_fields": [Character.id],
        "order_fields": [Character.name],
        "join_fields": [Product.character],
        "where_field": Character.name,
        "by_range": False,
        "range": 0,
        "range_step": 0,
        "digits_after_dot": 0,
        "message_text": "Выберите характеристики",
    },
    3: {
        "query_fields": [Product.power],
        "button_fields": ["callback_data", "label"],
        "group_fields": [Product.power],
        "order_fields": [Product.power],
        "join_fields": [],
        "where_field": Product.power,
        "by_range": True,
        "range": 0.4,
        "range_step": 0.1,
        "digits_after_dot": 1,
        "message_text": "Выберите диапазон мощности охлаждения (кВт)",
    },
    4: {
        "query_fields": [Brand.id, Brand.name],
        "button_fields": ["callback_data", "label"],
        "group_fields": [Brand.id],
        "order_fields": [Brand.name],
        "join_fields": [Product.brand],
        "where_field": Brand.name,
        "by_range": False,
        "range": 0,
        "range_step": 0,
        "digits_after_dot": 0,
        "message_text": "Выберите бренд",
    },
    5: {
        "query_fields": [
            Product.id,
            Product.model,
            Product.description,
            Product.pdf_url,
            Product.image_url,
        ],
        "button_fields": [
            "callback_data",
            "label",
            "description",
            "pdf_url",
            "image_url",
        ],
        "group_fields": [Product.id],
        "order_fields": [Product.model],
        "join_fields": [],
        "where_field": Product.model,
        "by_range": False,
        "range": 0,
        "range_step": 0,
        "digits_after_dot": 0,
        "message_text": "Выберите модели",
    },
    6: {
        "query_fields": [
            Product.id,
            Product.model,
            Product.description,
            Product.pdf_url,
            Product.image_url,
        ],
        "button_fields": [
            "model_id",
            "model",
            "description",
            "pdf_url",
            "image_url",
        ],
        "group_fields": [Product.id],
        "order_fields": [Product.model],
        "join_fields": [],
        "where_field": Product.model,
        "by_range": False,
        "range": 0,
        "range_step": 0,
        "digits_after_dot": 0,
        "message_text": "Ваш выбор",
    },
}

# словарь состояний множественного выбора. ОТКЛЮЧАТЬ и ВКЛЮЧАТЬ ТУТ
MULTIPLE_STEP = {
    1: False,  # select_category # всегда False, не трогать
    2: True,  # select_type
    3: True,  # select_power
    4: True,  # select_brand
    5: False,  # select_model # всегда False, не трогать
    6: False,  # show_model_info # всегда False, не трогать
}

MULTIPLE_STEP_HANDLER = {
    "select_category": 1,  # select_category
    "select_type": 2,  # select_type
    "select_power": 3,  # select_power
    "select_brand": 4,  # select_brand
    "select_model": 5,  # select_model
    "show_model_info": 6,
}

MULTIPLE_STEP_SELECTION_KEY = {
    "category": 1,  # 1 state select_category
    "type": 2,  # 2 select_type
    "power": 3,  # 3 select_power
    "brand": 4,  # 4 select_brand
    "model": 5,  # 5 select_model
}

HANDLE_PAGINATOR_PATTERN = r"^(prev|next)_[0-9]+$"
# кол-во элементов на страницу для пагинатора
ITEMS_PER_PAGE = 2
# Список названий состояний-функций
STATE_NAMES = [
    "select_category",
    "select_type",
    "select_power",
    "select_brand",
    "select_model",
    "show_result",
]
