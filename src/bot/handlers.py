import json
import logging

import telegram.error
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from bot.database import fetch_data_from_db
from bot.multiple_choice import (
    check_multi_dict,
    get_multiple_elem_buttons,
    get_next_step_button,
    get_selected_dict,
    get_selected_values,
    update_multiple_dict,
)
from bot.paginator import (
    check_paginator,
    check_string,
    create_paginator_dict,
    get_paginator_elements,
)
from bot.statistics_func import increment_view_stats
from bot.utils import clear_pagination_state, load_previous_state, save_state
from bot.variables import (
    MULTIPLE_STEP,
    MULTIPLE_STEP_HANDLER,
    MULTIPLE_STEP_SELECTION_KEY,
    SELECT_BRAND,
    SELECT_CATEGORY,
    SELECT_MODEL,
    SELECT_POWER,
    SELECT_TYPE,
    SHOW_RESULT,
    STATE_NAMES,
)
from db.core import async_session_factory

logger = logging.getLogger(__name__)


def get_elem_buttons(session_key, current_elements):
    """Создает кнопки без множественного выбора."""
    return [
        [
            InlineKeyboardButton(
                str(elem["model"] if isinstance(elem, dict) else elem),
                callback_data=(
                    f"{session_key}_"
                    f"{elem['model'] if isinstance(elem, dict) else elem}"
                ),
            )
        ]
        for elem in current_elements
    ]


def create_keyboard(
    buttons: list[list[InlineKeyboardButton]],
    paginator_buttons: list[list[InlineKeyboardButton]] = None,
    add_navigation_buttons: bool = True,
) -> InlineKeyboardMarkup:
    """
    Создает клавиатуру с кнопками и добавляет кнопки пагинации и навигации.

    :param buttons: Список кнопок для клавиатуры.
    :param paginator_buttons: Список кнопок пагинации, если есть.
    :param add_navigation_buttons: Флаг, указывающий, нужно ли добавлять
    кнопки "Назад" и "В начало".
    :return: Объект InlineKeyboardMarkup с разметкой клавиатуры.
    """
    logger.info("Создание клавиатуры с кнопками и навигацией.")
    keyboard = buttons if buttons else []
    if paginator_buttons:
        keyboard.extend([paginator_buttons])
    if add_navigation_buttons:
        keyboard.append(
            [
                InlineKeyboardButton("Назад", callback_data="back"),
                InlineKeyboardButton("В начало", callback_data="start"),
            ]
        )
    return InlineKeyboardMarkup(keyboard)


async def send_message(
    update: Update, text: str, reply_markup: InlineKeyboardMarkup
):
    """
    Отправляет или редактирует сообщение с текстом и клавиатурой.

    :param update: Объект Update, представляющий текущее обновление
    от Telegram.
    :param text: Текст сообщения.
    :param reply_markup: Разметка клавиатуры.
    :return: None
    """
    user = (
        update.message.from_user
        if update.message
        else update.callback_query.from_user
    )
    logger.info(
        f"Отправка сообщения пользователю "
        f"{user.first_name} ({user.id}). Текст: {text}"
    )

    if update.message:
        await update.message.reply_text(text, reply_markup=reply_markup)
    else:
        await update.callback_query.edit_message_text(
            text, reply_markup=reply_markup
        )


def serialize_reply_markup(reply_markup):
    """Сериализует клавиатуру для точного сравнения."""
    if reply_markup is None:
        return None
    return json.dumps(reply_markup.to_dict(), sort_keys=True)


async def handle_selection(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    session_key: str,
    message_text: str,
    state: int,
    handler_name: str,
) -> int:
    """Обрабатывает выбор эл-та и отображает доступные опции с пагинацией."""
    # user = update.callback_query.from_user
    query = update.callback_query
    await query.answer()

    # Определяем текущий номер шага на основе handler_name
    current_step_number = MULTIPLE_STEP_HANDLER[handler_name]
    # Словарь множественного выбора
    multiple_dict = context.chat_data.get("multiple", {})
    selected_dict = get_selected_dict(multiple_dict, state)

    # Универсальная функция для всех хендлеров
    async with async_session_factory() as session:
        # Вызываем fetch_data_from_db напрямую и получаем результат
        result = await fetch_data_from_db(
            session, selected_dict, current_step_number
        )
        elements = result["buttons"]  # Извлекаем список кнопок
        message_text = result["message_text"]  # Извлекаем текст сообщения

    # Блок пагинации
    if (
        not query.data.startswith("next_")
        and not query.data.startswith("prev_")
        and not query.data.startswith("multiple")
    ):
        clear_pagination_state(context)
    if "pagination" not in context.user_data:
        context.user_data["pagination"] = create_paginator_dict()

    (current_elements, paginator_buttons, pagination_dict) = (
        get_paginator_elements(
            context.user_data["pagination"], state - 1, elements
        )
    )
    context.user_data["pagination"] = pagination_dict
    # Конец блока пагинации
    # Обработка ответа кнопки выбора
    callback_data = update.callback_query.data.split("_")
    param = callback_data[-1]
    command = callback_data[0]

    # Обновляем multiple_dict, если нужно
    if command not in ["back", "start"]:
        if MULTIPLE_STEP[current_step_number]:
            if (
                command in MULTIPLE_STEP_SELECTION_KEY
                and MULTIPLE_STEP_SELECTION_KEY[command] == current_step_number
            ) or command == "multiple":
                if (
                    not check_paginator(update.callback_query.data)
                    and len(callback_data) > 1
                ):
                    context.chat_data["multiple"] = update_multiple_dict(
                        multiple_dict, current_step_number, param
                    )

    # Формирование новых кнопок
    if MULTIPLE_STEP[current_step_number]:
        # Формирование кнопок множественного выбора
        element_buttons = get_multiple_elem_buttons(
            multiple_dict,
            session_key,
            current_elements,
            current_step_number,
        )
        next_step_button = get_next_step_button()  # кнопка к следующему шагу
        element_buttons.append(next_step_button)
    else:
        element_buttons = get_elem_buttons(session_key, current_elements)

    # Создаем новую клавиатуру
    new_reply_markup = create_keyboard(element_buttons, paginator_buttons)

    # Обновляем сообщение и клавиатуру
    current_message = query.message.text
    current_reply_markup = serialize_reply_markup(query.message.reply_markup)
    new_reply_markup_serialized = serialize_reply_markup(new_reply_markup)

    if (
        current_message != message_text
        or current_reply_markup != new_reply_markup_serialized
    ):
        save_state(
            context,
            state,
            message_text,
            new_reply_markup,
            handler_name=handler_name,
        )
        try:
            await query.edit_message_text(
                message_text, reply_markup=new_reply_markup
            )
        except telegram.error.BadRequest as e:
            logger.warning(f"Ошибка при редактировании сообщения: {e}")

    # Логика перехода между состояниями
    if (
        MULTIPLE_STEP[MULTIPLE_STEP_HANDLER[handler_name]]
        or command == "multiple"
    ) and command != "step-forward":
        return state - 1
    elif command == "step-forward":
        if (
            not MULTIPLE_STEP[MULTIPLE_STEP_HANDLER[handler_name]]
            and MULTIPLE_STEP[MULTIPLE_STEP_HANDLER[handler_name] - 1]
        ):
            return state
        else:
            return state - 1
    return state


async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    return_to_main_menu: bool = False,
) -> int:
    """
    Инициирует взаимодействие с пользователем и показывает главное меню.

    :param update: Объект Update, представляющий текущее обновление
    от Telegram.
    :param context: Контекст вызова, содержащий данные пользователя.
    :param return_to_main_menu: Флаг, указывающий, следует ли возвращаться
    в главное меню.
    :return: Состояние SELECT_CATEGORY для перехода к выбору категории.
    """
    user = (
        update.message.from_user
        if update.message
        else update.callback_query.from_user
    )
    logger.info(
        f"Пользователь {user.first_name} ({user.id})" "инициирует старт."
    )
    # Инициируем словарь в контексте для хранения данных пагинации
    context.user_data["pagination"] = create_paginator_dict()
    # Инициируем словарь в контексте для хранения множественного выбора
    context.chat_data["multiple"] = {}

    # Упрощаем сообщение для возврата в главное меню
    greeting_text = (
        "Вы вернулись в главное меню."
        if return_to_main_menu
        else "Добрый день! Введите ваш запрос или выберите действие "
        "из предложенных кнопок."
    )

    main_menu_buttons = [
        [InlineKeyboardButton("О боте", callback_data="about")],
        [
            InlineKeyboardButton(
                "Выбрать категорию", callback_data="select-category"
            )
        ],
    ]
    reply_markup = InlineKeyboardMarkup(main_menu_buttons)
    save_state(context, SELECT_CATEGORY, greeting_text, reply_markup)

    await send_message(update, greeting_text, reply_markup)
    return SELECT_CATEGORY


async def show_about(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """
    Показывает информацию о боте и его функциях.

    :param update: Объект Update, представляющий текущее обновление
    от Telegram.
    :param context: Контекст вызова, содержащий данные пользователя.
    :return: Состояние SELECT_CATEGORY для выбора категории.
    """
    user = update.callback_query.from_user
    logger.info(
        f"Пользователь {user.first_name} ({user.id}) "
        f"запрашивает информацию о боте."
    )

    query = update.callback_query
    await query.answer()

    about_text = (
        "Этот бот предназначен для помощи в выборе и покупке кондиционеров "
        "и другой техники.\n"
        "Вы можете использовать его для:\n\n"
        "1. *Выбора категории товаров* - просто выберите "
        "интересующую вас категорию.\n"
        "2. *Подбора подходящего оборудования* - выберите тип и бренд, "
        "чтобы найти оптимальные модели.\n"
        "3. *Получения информации о моделях* - просмотрите краткое описание "
        "и откройте подробные данные по каждой модели.\n\n"
        "Используйте меню, чтобы начать или вернуться в главное меню "
        "в любое время."
    )

    reply_markup = create_keyboard([])
    save_state(context, SELECT_CATEGORY, about_text, reply_markup)

    await query.edit_message_text(
        about_text, reply_markup=reply_markup, parse_mode="Markdown"
    )
    return SELECT_CATEGORY


async def select_category(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """
    Переход к выбору категории товаров.

    :param update: Объект Update, представляющий текущее обновление
    от Telegram.
    :param context: Контекст вызова, содержащий данные пользователя.
    :return: Состояние SELECT_TYPE для выбора типа товаров.
    """
    user = update.callback_query.from_user
    logger.info(
        f"Пользователь {user.first_name} ({user.id})" "выбирает категорию."
    )
    # Инициируем словарь в контексте для хранения множественного выбора
    context.chat_data["multiple"] = {}

    return await handle_selection(
        update,
        context,
        session_key="category",
        message_text="Выберите категорию",
        state=SELECT_TYPE,
        handler_name="select_category",
    )


async def select_type(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """
    Переход к выбору типа товаров в выбранной категории.

    :param update: Объект Update, представляющий текущее обновление
    от Telegram.
    :param context: Контекст вызова, содержащий данные пользователя.
    :return: Состояние SELECT_BRAND для выбора бренда.
    """
    user = update.callback_query.from_user
    multiple_dict = context.chat_data.get("multiple", {})
    if update.callback_query.data == "back":
        selected_category = get_selected_values(multiple_dict.get(1, {}))
    else:
        # проверка что "не внутри пагинатора"
        selected_category = check_string(
            update.callback_query.data,
            context.chat_data["multiple"].get("1", None),
        )

    if update.callback_query.data != "back":
        if not check_multi_dict(multiple_dict, 1):
            context.chat_data["multiple"] = update_multiple_dict(
                multiple_dict, 1, selected_category
            )
    logger.info(
        f"Пользователь {user.first_name}"
        f" ({user.id}) выбирает тип для категории: {selected_category}"
    )

    return await handle_selection(
        update,
        context,
        session_key="type",
        message_text="Выберите тип",
        state=SELECT_POWER,
        handler_name="select_type",
    )


async def select_power(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """
    Переход к выбору мощности товара в выбранной категории и типе.

    :param update: Объект Update, представляющий текущее обновление
    от Telegram.
    :param context: Контекст вызова, содержащий данные пользователя.
    :return: Состояние SELECT_BRAND для выбора бренда товара.
    """
    user = update.callback_query.from_user
    multiple_dict = context.chat_data.get("multiple", {})
    # проверка что "не внутри пагинатора"
    if update.callback_query.data == "back":
        selected_type = get_selected_values(multiple_dict.get(2, {}))
    else:
        selected_type = check_string(
            update.callback_query.data,
            get_selected_values(multiple_dict.get(2, {})),
        )
    logger.info(
        f"Пользователь {user.first_name} ({user.id}) "
        f"выбирает мощность для типа: {selected_type}"
    )

    if update.callback_query.data != "back":
        if not check_multi_dict(multiple_dict, 2):
            context.chat_data["multiple"] = update_multiple_dict(
                multiple_dict, 2, selected_type
            )
    logger.info(
        f"Пользователь {user.first_name} ({user.id}) "
        f"выбирает мощность для типа: {selected_type}"
    )
    return await handle_selection(
        update,
        context,
        session_key="power",
        message_text="Выберите мощность",
        state=SELECT_BRAND,
        handler_name="select_power",
    )


async def select_brand(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """
    Переход к выбору бренда товара в выбранной категории и типе.

    :param update: Объект Update, представляющий текущее обновление
    от Telegram.
    :param context: Контекст вызова, содержащий данные пользователя.
    :return: Состояние SELECT_MODEL для выбора модели.
    """
    user = update.callback_query.from_user
    multiple_dict = context.chat_data.get("multiple", {})
    # проверка что "не внутри пагинатора"
    selected_power = check_string(
        update.callback_query.data,
        context.chat_data["multiple"].get("3", None),
    )
    logger.info(
        f"Пользователь {user.first_name} ({user.id}) выбирает бренд "
        f"для типа: {selected_power}"
    )

    if not check_multi_dict(multiple_dict, 3):
        context.chat_data["multiple"] = update_multiple_dict(
            multiple_dict, 3, selected_power
        )
    return await handle_selection(
        update,
        context,
        session_key="brand",
        message_text="Выберите бренд",
        state=SELECT_MODEL,
        handler_name="select_brand",
    )


async def select_model(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """
    Переход к выбору модели товара на основе бренда, типа и категории.

    :param update: Объект Update, представляющий текущее обновление
    от Telegram.
    :param context: Контекст вызова, содержащий данные пользователя.
    :return: Состояние SHOW_RESULT для отображения результата.
    """
    user = update.callback_query.from_user
    multiple_dict = context.chat_data.get("multiple", {})
    # проверка что "не внутри пагинатора"
    selected_brand = check_string(
        update.callback_query.data,
        context.chat_data["multiple"].get("4", None),
    )
    logger.debug(f"Selected brand: {selected_brand}")
    logger.info(
        f"Пользователь {user.first_name} ({user.id}) "
        f"выбирает модель для бренда: {selected_brand}, "
    )

    if not check_multi_dict(multiple_dict, 4):
        context.chat_data["multiple"] = update_multiple_dict(
            multiple_dict, 4, selected_brand
        )

    return await handle_selection(
        update,
        context,
        session_key="model",
        message_text="Выберите модель",
        state=SHOW_RESULT,
        handler_name="select_model",
    )


async def show_model_info(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """
    Отображает инф-цию о выбранном товаре, ссылку на PDF и изображение.

    :param update: Объект Update, представляющий тек. обновление от Telegram.
    :param context: Контекст вызова, содержащий данные пользователя.
    :return: Состояние SELECT_CATEGORY для возврата в меню категорий.
    """
    user = update.callback_query.from_user
    model_id = check_string(
        update.callback_query.data,
        context.user_data.get("selected_model", None),
    )
    logger.info(
        f"Пользователь {user.first_name} ({user.id}) запрашивает "
        f"информацию о модели {model_id}"
    )

    async with async_session_factory() as session:
        # Собираем словарь с выбранными значениями по шагам
        multiple_dict = context.chat_data.get("multiple", {})
        selected_dict = get_selected_dict(multiple_dict, 5)

        try:
            # Получаем данные о модели с помощью функции fetch_data_from_db
            # Шаг 5 — выбор модели
            result = await fetch_data_from_db(session, selected_dict, 5)
        except ValueError as e:
            logger.error(f"Ошибка при получении данных о модели: {e}")
            await update.callback_query.edit_message_text(
                "Произошла ошибка при получении данных о модели."
            )
            return SELECT_CATEGORY

        models = result["buttons"]  # Список моделей

    selected_model = next(
        (model for model in models if model["label"] == model_id), None
    )

    # Проверка, что модель найдена
    if not selected_model:
        logger.warning(
            f"Модель с идентификатором {model_id} не найдена "
            f"для пользователя {user.first_name} ({user.id})"
        )
        await update.callback_query.edit_message_text(
            f"Модель с идентификатором {model_id} не найдена."
        )
        return SELECT_CATEGORY

    # Формируем текст сообщения с информацией о модели
    text = (
        f'Название: {selected_model["label"]}\n'
        f'Описание: {selected_model["description"]}\n\n'
        f"Спасибо за использование бота!"
    )
    # Увеличиваем счетчик статистики (просмотров)
    async with async_session_factory() as session:
        await increment_view_stats(session, selected_model["callback_data"])

    # Получаем ссылку на изображение из БД
    image_url = selected_model.get("image_url")

    # Создаем клавиатуру для кнопки со ссылкой на PDF
    reply_markup = InlineKeyboardMarkup(
        [[InlineKeyboardButton("Открыть PDF", url=selected_model["pdf_url"])]]
    )

    # Удаляем старое сообщение с выбором модели
    await update.callback_query.delete_message()

    # Отправляем изображение модели, если есть URL
    try:
        await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=image_url,
            caption=text,
            reply_markup=reply_markup,
        )
    except Exception as e:
        logger.error(f"Ошибка при отправке изображения: {e}")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"Ошибка при отправке изображения: {e}",
            reply_markup=reply_markup,
        )

    # Отправляем второе сообщение с кнопками "О боте" и "Выбрать категорию"
    main_menu_buttons = [
        [InlineKeyboardButton("О боте", callback_data="about")],
        [
            InlineKeyboardButton(
                "Выбрать категорию", callback_data="select-category"
            )
        ],
    ]
    reply_markup_main_menu = InlineKeyboardMarkup(main_menu_buttons)

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Вы вернулись в главное меню.",
        reply_markup=reply_markup_main_menu,
    )

    return SELECT_CATEGORY


async def handle_back(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """
    Обрабатывает нажатие кнопки "Назад" к предыдущему состоянию.

    :param update: Объект Update, представляющий
    текущее обновление от Telegram.
    :param context: Контекст вызова, содержащий данные пользователя.
    :return: Предыдущее состояние пользователя или SELECT_CATEGORY,
    если состояние не найдено.
    """
    user = update.callback_query.from_user
    previous_state = load_previous_state(context)

    if previous_state:
        logger.info(
            f"Пользователь {user.first_name} "
            f"({user.id}) возвращается к предыдущему состоянию."
        )

        # Очищаем состояние пагинации
        clear_pagination_state(context)

        # Восстанавливаем параметр пагинации
        context.user_data["pagination"] = create_paginator_dict()
        (context.user_data["pagination"]["name_parameter"]) = (
            previous_state.get("handler_name")
        )
        # Возвращаем состояние множественного выбора к предыдущему шагу
        if "multiple" in previous_state:
            context.chat_data["multiple"] = previous_state["multiple"]

        handler_name = previous_state.get("handler_name")

        # Возвращаем пользователю предыдущее сообщение и клавиатуру
        if handler_name:
            return await PAGINATION_HANDLER[handler_name](update, context)
        else:
            # Если handler_name не найден, просто возвращаем состояние
            await update.callback_query.edit_message_text(
                previous_state["message_text"],
                reply_markup=previous_state["reply_markup"],
            )
            return previous_state["state"]

    logger.warning(
        f"Пользователь {user.first_name} "
        f"({user.id}) пытается вернуться назад, "
        f"но состояние не найдено."
    )
    await update.callback_query.answer(
        "Нет предыдущего состояния для возврата."
    )
    return SELECT_CATEGORY


async def handle_start(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """
    Обрабатывает команду /start и возвращает пользователя в главное меню.

    :param update: Объект Update, представляющий текущее обновление
    от Telegram.
    :param context: Контекст вызова, содержащий данные пользователя.
    :return: Состояние SELECT_CATEGORY для возврата в главное меню.
    """
    user = (
        update.message.from_user
        if update.message
        else update.callback_query.from_user
    )
    logger.info(
        f"Пользователь {user.first_name} ({user.id})"
        f" возвращается в главное меню."
    )
    return await start(update, context, return_to_main_menu=True)


# блок пагинации
# словарь функций-обработчиков, надо будет переместить
PAGINATION_HANDLER = {
    "select_category": select_category,
    "select_power": select_power,
    "select_model": select_model,
    "select_brand": select_brand,
    "select_type": select_type,
    "show_result": show_model_info,
}


async def handle_no_answer(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Обрабатывает команду "N из M стр." и возвращает пустой ответ."""
    query = update.callback_query
    await query.answer()


async def handle_pagination(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Обрабатывает команды пагинатора."""
    query = update.callback_query
    await query.answer()
    # Проверяем наличие состояния пагинации, если его нет — инициализируем
    if "pagination" not in context.user_data:
        context.user_data["pagination"] = create_paginator_dict()

    current_page = context.user_data["pagination"].get("current_page", 0)
    name_parameter = context.user_data["pagination"].get("name_parameter")

    if "prev_" in query.data:
        current_page = max(0, current_page - 1)
    elif "next_" in query.data:
        current_page += 1

    # Сохраняем новую страницу в состоянии пагинации
    context.user_data["pagination"]["current_page"] = current_page

    # Запуск функции обработчика для текущего параметра
    if name_parameter:
        await PAGINATION_HANDLER[name_parameter](update, context)
    else:
        logger.warning("Не найден параметр для пагинации.")


async def handle_step_forward(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Переходит на следующий этап отбора."""
    query = update.callback_query
    await query.answer()
    state = context.user_data["history"][-1]["state"]
    return await PAGINATION_HANDLER[STATE_NAMES[state]](update, context)
